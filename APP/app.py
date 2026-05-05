from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, make_response
import os
import sys

# Add the current directory to sys.path to allow imports from local modules (forms, ai_question_generator, etc.)
# This ensures that imports work both locally and when deployed on Render.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_required
from flask_wtf.csrf import CSRFProtect
from forms import LoginForm, SignupForm
from sqlalchemy import func
from sqlalchemy import Column, Integer, Text, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
import random
from sqlalchemy import func
from datetime import datetime
from typing import Optional, Dict, Any
from flask import session
from datetime import timedelta
import pdfkit
from flask_login import login_required, current_user, login_user, logout_user
import traceback
import secrets
from flask_mail import Mail, Message
from dotenv import load_dotenv
from ai_question_generator import (
    generate_questions_from_ai,
    get_topic_for_level,
    get_random_difficulty,
    LEVEL_TOPIC_MAP,
    SUBJECT_TOPICS
)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Force UTF-8 output on Windows to avoid charmap encoding errors in print()
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

login_manager = LoginManager(app)
login_manager.login_view = 'login'

load_dotenv()
csrf = CSRFProtect(app)

WKHTMLTOPDF_PATH = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
try:
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
except OSError:
    config = None
    print("[Warning] wkhtmltopdf not found — PDF certificate generation will be unavailable.")

# Configure database — reads from .env (TiDB Cloud or any MySQL-compatible cloud)
_db_uri = os.getenv('DATABASE_URI', 'mysql+pymysql://root:Snehi@localhost/quizie')
app.config['SQLALCHEMY_DATABASE_URI'] = _db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# TiDB Cloud requires SSL; these engine options are ignored for plain local MySQL
if 'tidb' in _db_uri or 'tidbcloud' in _db_uri:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {
            'ssl': {'ssl_disabled': False}
        },
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }
else:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }
app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF protection globally

mail = None  # Define global mail variable
def test_mail_config():
    """Test the email configuration"""
    try:
        with app.app_context():
            # Print current mail configuration (excluding password)
            print("Current mail configuration:")
            print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
            print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
            print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
            print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
            print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
            
            if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
                print("Error: Missing email credentials in configuration")
                return False
                
            # Test connection to SMTP server
            mail.connect()
            print("Successfully connected to SMTP server")
            return True
            
    except Exception as e:
        print(f"Mail configuration test failed: {str(e)}")
        return False

def init_app():
    global mail
    mail = configure_mail(app)
    if test_mail_config():
        print("Email configuration test successful")
    else:
        print("Email configuration test failed - check your .env file and Gmail settings")

def configure_mail(app):
    """Configure Flask-Mail with secure Gmail settings"""
    try:
        app.config.update(
            MAIL_SERVER='smtp.gmail.com',
            MAIL_PORT=587,
            MAIL_USE_TLS=True,
            MAIL_USE_SSL=False,
            MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
            MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
            MAIL_DEFAULT_SENDER=os.getenv('MAIL_USERNAME'),
            MAIL_MAX_EMAILS=None,
            MAIL_ASCII_ATTACHMENTS=False,
            MAIL_DEBUG=True
        )
        return Mail(app)
    except Exception as e:
        print(f"Mail configuration error: {str(e)}")
        return None

def verify_mail_config():
    """Test email configuration and authentication"""
    try:
        # Get credentials from environment
        username = os.getenv('MAIL_USERNAME')
        password = os.getenv('MAIL_PASSWORD')
        
        # Basic validation
        if not username or not password:
            print("Error: Missing email credentials in environment variables")
            print(f"Username present: {'Yes' if username else 'No'}")
            print(f"Password present: {'Yes' if password else 'No'}")
            return False
            
        if not username.endswith('@gmail.com'):
            print("Error: MAIL_USERNAME must be a Gmail address")
            return False
            
        if len(password) != 16:
            print("Warning: Password length suggests this might not be an App Password")
            print("Please ensure you're using an App Password from Google Account settings")
            
        return True
        
    except Exception as e:
        print(f"Configuration verification error: {str(e)}")
        return False

def send_test_email(mail):
    """Send a test email to verify configuration"""
    try:
        recipient = os.getenv('MAIL_USERNAME')  # Send to self for testing
        msg = Message(
            subject='Test Email - Flask App',
            recipients=[recipient],
            body='This is a test email to verify SMTP configuration.'
        )
        mail.send(msg)
        print("Test email sent successfully!")
        return True
    except Exception as e:
        print(f"Test email error: {str(e)}")
        return False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Models
class MathQuestion(db.Model):
    __tablename__ = 'math_questions'
    
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    correct = db.Column(db.Text, nullable=False)
    incorrect1 = db.Column(db.Text, nullable=False)
    incorrect2 = db.Column(db.Text, nullable=False)
    incorrect3 = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.Enum('Easy', 'Medium', 'Hard'), nullable=False)
    topic_name = db.Column(db.Enum(
        'Matrices', 'Determinant', 'Function', 'Limit', 'Logarithm',
        'Trigonometry', 'Vectors', 'Coordinate Geometry',
        'Differentiation', 'Integration'
    ), nullable=False)

class PhysicsQuestion(db.Model):
    __tablename__ = 'physics_questions'
    
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    correct = db.Column(db.Text, nullable=False)
    incorrect1 = db.Column(db.Text, nullable=False)
    incorrect2 = db.Column(db.Text, nullable=False)
    incorrect3 = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.Enum('Easy', 'Medium', 'Hard'), nullable=False)
    topic_name = db.Column(db.Enum(
        'Units and measurements','Heat and thermometry','Laws of Motion',
        'work and energy','Electric current','Wave option, optics and acoustics'
    ), nullable=False)


class ChemistryQuestion(db.Model):
    __tablename__ = 'chemistry_questions'
    
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    correct = db.Column(db.Text, nullable=False)
    incorrect1 = db.Column(db.Text, nullable=False)
    incorrect2 = db.Column(db.Text, nullable=False)
    incorrect3 = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.Enum('Easy', 'Medium', 'Hard'), nullable=False)
    topic_name = db.Column(db.Enum(
        'Chemical reactions and equations','Acid, Base and Salts','Metals and Non-metals'
    ), nullable=False)

class EnglishQuestion(db.Model):
    __tablename__ = 'english_questions'
    
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    correct = db.Column(db.Text, nullable=False)
    incorrect1 = db.Column(db.Text, nullable=False)
    incorrect2 = db.Column(db.Text, nullable=False)
    incorrect3 = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.Enum('Easy', 'Medium', 'Hard'), nullable=False)
    topic_name = db.Column(db.Enum(
        'Comprehension of Unseen Passage', 'Theory of Communication', 'Techniques of Writing', 'Grammar', 
        'Correction of incorrect words and sentences'
    ), nullable=False)

class ComputerQuestion(db.Model):
    __tablename__ = 'computer_questions'
    
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    correct = db.Column(db.Text, nullable=False)
    incorrect1 = db.Column(db.Text, nullable=False)
    incorrect2 = db.Column(db.Text, nullable=False)
    incorrect3 = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.Enum('Easy', 'Medium', 'Hard'), nullable=False)
    topic_name = db.Column(db.Enum(
        'Basics of Computer System', 'Introduction to Internet HTML', 'MS-Word',
        ' MS-Excel', ' MS-Power Point',
    ), nullable=False)

class EnvironmentQuestion(db.Model):
    __tablename__ = 'environment_questions'
    
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    correct = db.Column(db.Text, nullable=False)
    incorrect1 = db.Column(db.Text, nullable=False)
    incorrect2 = db.Column(db.Text, nullable=False)
    incorrect3 = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.Enum('Easy', 'Medium', 'Hard'), nullable=False)
    topic_name = db.Column(db.Enum(
        'Ecosystem', 'Pollution and its types', 'Climate Change', 'Renewable Energy'
    ), nullable=False)


class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserLevel(db.Model):
    __tablename__ = 'user_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    performance = db.Column(db.Float, nullable=True)
    badges = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    levels = db.relationship('UserLevel', backref='user', lazy=True)
    attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    avatar = db.Column(db.String(100), default='avatar1.jpg')

class QuestionAttempt(db.Model):
    __tablename__ = 'question_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    # Store options as a JSON array
    options = db.Column(db.JSON, nullable=False)  # Will store array of all options
    selected = db.Column(db.Text, nullable=True)  # Store the selected option value
    is_correct = db.Column(db.Boolean, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    quiz_attempt = db.relationship('QuizAttempt', backref='question_attempts')

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='password_resets')

# Question mapping for different subjects
QUESTION_MODELS = {
    'math': MathQuestion,
    'physics': PhysicsQuestion,
    'chemistry': ChemistryQuestion,
    'english': EnglishQuestion,
    'computer': ComputerQuestion,
    'environment': EnvironmentQuestion
}

AVAILABLE_SUBJECTS = {
    'math': {
        'name': 'Mathematics',
        'template': 'math-quiz.html'
    },
    'physics': {
        'name': 'Physics',
        'template': 'physics-quiz.html'
    },
    
    'chemistry': {
        'name': 'Chemistry',
        'template': 'chemistry-quiz.html'
    },

    'english': {
        'name': 'English',
        'template': 'english-quiz.html'
    },

    'computer': {
        'name': 'Computer Practices',
        'template': 'computer-quiz.html'
    }, 

    'environment': {
        'name': 'Environmental Science',
        'template': 'environment-quiz.html'
    }
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/debug-questions')
@login_required
def debug_questions():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        connection_status = "Database connection successful"
        
        # Check each subject's questions
        questions_info = {}
        for subject, model in QUESTION_MODELS.items():
            count = model.query.count()
            sample = model.query.first()
            questions_info[subject] = {
                'count': count,
                'sample': sample.__dict__ if sample else None
            }
            
        return jsonify({
            'connection_status': connection_status,
            'questions_info': questions_info
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Database error: {str(e)}'
        }), 500

def get_adaptive_questions(user_id, subject, level, amount=10):
    """
    Smart adaptive question fetcher:
    1. Determines the topic for this level.
    2. Excludes questions the user already answered CORRECTLY (no repeat).
    3. Incorrectly answered questions CAN reappear for reinforcement.
    4. If DB doesn't have enough fresh questions, generates new ones via Gemini AI
       and saves them to the DB for future use.
    """
    print(f"[Adaptive] user={user_id}, subject={subject}, level={level}, amount={amount}")

    try:
        QuestionModel = QUESTION_MODELS.get(subject.lower())
        if not QuestionModel:
            print(f"[Adaptive] Unknown subject: {subject}")
            return []

        # -- Determine topic and difficulty for this level ----------------------
        topic = get_topic_for_level(subject.lower(), int(level))
        difficulty = get_random_difficulty()
        print(f"[Adaptive] Level {level} -> topic='{topic}', difficulty='{difficulty}'")

        # -- Get IDs of questions this user already answered CORRECTLY ----------
        correctly_answered_ids = db.session.query(
            QuestionAttempt.question_id
        ).join(QuizAttempt).filter(
            QuizAttempt.user_id == user_id,
            QuestionAttempt.subject == subject.lower(),
            QuestionAttempt.is_correct == True
        ).distinct().all()
        exclude_ids = [row[0] for row in correctly_answered_ids]
        print(f"[Adaptive] Excluding {len(exclude_ids)} correctly answered question IDs")

        # -- Fetch questions for this topic from DB, excluding correct ones -----
        query = QuestionModel.query.filter(
            QuestionModel.topic_name == topic
        )
        if exclude_ids:
            query = query.filter(~QuestionModel.question_id.in_(exclude_ids))
        available = query.order_by(func.rand()).limit(amount).all()
        print(f"[Adaptive] Found {len(available)} usable questions in DB")

        # -- Generate more via AI if not enough --------------------------------
        if len(available) < amount:
            needed = amount - len(available)
            existing_ids = {q.question_id for q in available}
            print(f"[Adaptive] Need {needed} more questions — calling Gemini AI")

            ai_questions = generate_questions_from_ai(
                subject=subject.lower(),
                topic=topic,
                difficulty=difficulty,
                count=needed + 3  # generate a few extra for variety
            )

            saved_count = 0
            for aq in ai_questions:
                if len(available) >= amount:
                    break
                try:
                    new_q = QuestionModel(
                        question=aq['question'],
                        correct=aq['correct'],
                        incorrect1=aq['incorrect1'],
                        incorrect2=aq['incorrect2'],
                        incorrect3=aq['incorrect3'],
                        solution=aq['solution'],
                        difficulty_level=aq.get('difficulty_level', difficulty),
                        topic_name=aq.get('topic_name', topic)
                    )
                    db.session.add(new_q)
                    db.session.flush()  # get the new question_id
                    if new_q.question_id not in existing_ids:
                        available.append(new_q)
                        existing_ids.add(new_q.question_id)
                        saved_count += 1
                except Exception as e:
                    print(f"[Adaptive] Error saving AI question: {e}")
                    db.session.rollback()
                    continue

            try:
                db.session.commit()
                print(f"[Adaptive] Saved {saved_count} new AI-generated questions to DB")
            except Exception as e:
                print(f"[Adaptive] DB commit error: {e}")
                db.session.rollback()

        # -- Format questions for frontend -------------------------------------
        formatted_questions = []
        for q in available[:amount]:
            options = [q.correct, q.incorrect1, q.incorrect2, q.incorrect3]
            random.shuffle(options)
            formatted_questions.append({
                'id': q.question_id,
                'question': q.question,
                'options': options,
                'correct_answer': q.correct,
                'solution': q.solution,
                'difficulty': q.difficulty_level,
                'topic': q.topic_name
            })

        print(f"[Adaptive] Returning {len(formatted_questions)} formatted questions")
        return formatted_questions

    except Exception as e:
        print(f"[Adaptive] Error: {e}")
        traceback.print_exc()
        return []

@app.route('/quiz/<subject>')
@login_required
def quiz(subject):
    if subject not in AVAILABLE_SUBJECTS:
        flash(f'Invalid subject. Available subjects are: {", ".join(AVAILABLE_SUBJECTS.keys())}')
        return redirect(url_for('home'))
    
    subject_info = AVAILABLE_SUBJECTS[subject]
    return render_template(
        subject_info['template'],
        subject=subject,
        subject_name=subject_info['name']
    )

@app.route('/home')
@login_required
def home():
    username = session.get('username') 
    return render_template('home.html', username=username)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        try:
            username = form.username.data
            email = form.email.data
            password = form.password.data
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return redirect(url_for('signup'))
            
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Registration successful', 'success')
            return redirect(url_for('home'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')  # Display the actual error
            print(f"Signup error: {e}")
            return redirect(url_for('signup'))
    else:
        # Print form errors for debugging
        print("Form validation errors:", form.errors)
            
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            email = form.email.data
            password = form.password.data
            
            user = User.query.filter_by(email=email).first()
           
            if user and check_password_hash(user.password, password):
                # This is the important line that was missing - use login_user
                login_user(user)
                
                # These session variables are fine to keep
                session['user_id'] = user.id
                session['username'] = user.username
                session['just_logged_in'] = True
                session['login_timestamp'] = datetime.now().strftime("%Y%m%d%H%M%S")
                print("User ID in session:", session.get('user_id'))
                return redirect(url_for('home'))
           
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))
           
        except Exception as e:
            print(f"Login error: {e}")
            flash('An error occurred during login', 'error')
            return redirect(url_for('login'))
           
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    # Add logout_user() call here
    logout_user()
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/leaderboard')
@login_required
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/api/leaderboard/<subject>')
def get_leaderboard(subject):
    try:
        if subject == 'all':
            # Get all users with their average scores across all subjects
            # First, get the average score for each user and subject
            user_subject_scores = db.session.query(
                UserLevel.user_id,
                UserLevel.subject,
                func.avg(UserLevel.score).label('avg_score')
            ).group_by(UserLevel.user_id, UserLevel.subject).all()
            
            # Create a dictionary to store scores by user
            user_scores = {}
            for record in user_subject_scores:
                if record.user_id not in user_scores:
                    user_scores[record.user_id] = {
                        'subject_scores': {},
                        'total_score': 0,
                        'subject_count': 0
                    }
                user_scores[record.user_id]['subject_scores'][record.subject] = record.avg_score
                user_scores[record.user_id]['total_score'] += record.avg_score
                user_scores[record.user_id]['subject_count'] += 1
            
            # Calculate average across subjects for each user
            for user_id in user_scores:
                user_scores[user_id]['average_score'] = (
                    user_scores[user_id]['total_score'] / user_scores[user_id]['subject_count']
                    if user_scores[user_id]['subject_count'] > 0 else 0
                )
            
            # Get user details and combine with scores
            users = User.query.all()
            leaderboard = []
            
            for user in users:
                if user.id in user_scores:
                    leaderboard.append({
                        'user_id': user.id,
                        'username': user.username,
                        'avatar': user.avatar,
                        'subject_scores': user_scores[user.id]['subject_scores'],
                        'average_score': user_scores[user.id]['average_score']
                    })
            
            # Sort by average score (descending)
            leaderboard.sort(key=lambda x: x['average_score'], reverse=True)
            
        else:
            # Get leaderboard for specific subject
            # Get all users who have attempted the subject
            user_scores = db.session.query(
                UserLevel.user_id,
                func.avg(UserLevel.score).label('avg_score')
            ).filter_by(subject=subject).group_by(UserLevel.user_id).all()
            
            # Get user details and combine with scores
            leaderboard = []
            for record in user_scores:
                user = User.query.get(record.user_id)
                if user:
                    leaderboard.append({
                        'user_id': user.id,
                        'username': user.username,
                        'avatar': user.avatar,
                        'subject_scores': {subject: record.avg_score},
                        'average_score': record.avg_score
                    })
            
            # Sort by average score (descending)
            leaderboard.sort(key=lambda x: x['average_score'], reverse=True)
        
        return jsonify({
            'users': leaderboard
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/level-info/<subject>/<int:level>')
@login_required
def level_info(subject, level):
    """Return the topic and difficulty info for a given subject/level."""
    subject = subject.lower()
    topic = get_topic_for_level(subject, level)
    topic_map = LEVEL_TOPIC_MAP.get(subject, {})
    # Build a list of all 50 levels with their topics for the sidebar
    all_levels = [
        {'level': lvl, 'topic': topic_map.get(lvl, '')}
        for lvl in range(1, 51)
    ]
    return jsonify({
        'level': level,
        'topic': topic,
        'all_levels': all_levels
    })


@app.route('/start-level', methods=['POST'])
@login_required
def start_level():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        level = data.get('level')
        subject = data.get('subject')

        if not all([level, subject]):
            return jsonify({'error': 'Missing required fields'}), 400

        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        # Get 10 adaptive questions for this level (topic-specific, no-repeat)
        questions = get_adaptive_questions(user_id, subject, level, amount=10)

        if not questions:
            print(f"Warning: No questions available for subject={subject}, level={level}")
            return jsonify({'error': 'No questions available. Please check your Gemini API key.'}), 404

        # Include topic in response so frontend can display it
        topic = get_topic_for_level(subject.lower(), int(level))
        return jsonify({
            'questions': questions,
            'level': level,
            'subject': subject,
            'topic': topic
        })

    except Exception as e:
        print(f"Start level error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Failed to start level: {str(e)}'}), 500

@app.route('/submit_level', methods=['POST'])
@login_required
def submit_level():
    try:
        # Log the raw request data
        data = request.get_json()
        print("=== DEBUG: Raw Request Data ===")
        print("Content-Type:", request.headers.get('Content-Type'))
        print("Request Data:", data)
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "details": "Request body is empty or not valid JSON"
            }), 400

        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                "error": "User not logged in",
                "details": "No user_id found in session"
            }), 401

        # Extract and validate required fields
        subject = data.get('subject')
        level = data.get('level')
        score = data.get('score')
        
        # Handle both formats of answer data
        question_responses = data.get('question_responses', [])
        answers = data.get('answers', {})

        print("=== DEBUG: Extracted Data ===")
        print(f"Subject: {subject}")
        print(f"Level: {level}")
        print(f"Score: {score}")
        print(f"Question Responses: {question_responses}")
        print(f"Answers: {answers}")

        # Validate required fields
        validation_errors = []
        if not subject:
            validation_errors.append("subject is required")
        if level is None:
            validation_errors.append("level is required")
        if score is None:
            validation_errors.append("score is required")
        if not question_responses and not answers:
            validation_errors.append("either question_responses or answers is required")

        if validation_errors:
            return jsonify({
                "error": "Validation failed",
                "details": validation_errors
            }), 400

        # Convert answers format to question_responses if needed
        if not question_responses and answers:
            question_responses = []
            QuestionModel = QUESTION_MODELS.get(subject.lower())
            if not QuestionModel:
                return jsonify({
                    "error": "Invalid subject",
                    "details": f"Subject {subject} not found in QUESTION_MODELS"
                }), 400

            for question_id, answer_data in answers.items():
                # Handle both boolean and object formats
                is_correct = answer_data if isinstance(answer_data, bool) else answer_data.get('is_correct')
                selected_option = answer_data.get('selected') if isinstance(answer_data, dict) else None

                question = QuestionModel.query.get(int(question_id))
                if question:
                    if selected_option is None:
                        selected_option = question.correct if is_correct else question.incorrect1
                    
                    question_responses.append({
                        'question_id': question_id,
                        'selected_option': selected_option,
                        'is_correct': is_correct
                    })

        print("=== DEBUG: Processed Question Responses ===")
        print(question_responses)

        # Create quiz attempt
        try:
            quiz_attempt = QuizAttempt(
                user_id=user_id,
                subject=subject,
                score=float(score),
                question_id=int(level)
            )
            db.session.add(quiz_attempt)
            db.session.flush()

            # Process each question response
            for response in question_responses:
                try:
                    question_id = int(response.get('question_id'))
                    selected_option = response.get('selected_option')
                    is_correct = response.get('is_correct', False)

                    QuestionModel = QUESTION_MODELS.get(subject.lower())
                    question = QuestionModel.query.get(question_id)
                    
                    if not question:
                        print(f"Warning: Question {question_id} not found")
                        continue

                    options = [
                        question.correct,
                        question.incorrect1,
                        question.incorrect2,
                        question.incorrect3
                    ]

                    question_attempt = QuestionAttempt(
                        quiz_attempt_id=quiz_attempt.id,
                        question_id=question_id,
                        options=options,
                        selected=selected_option,
                        is_correct=is_correct,
                        subject=subject
                    )
                    db.session.add(question_attempt)
                    
                except Exception as e:
                    print(f"Error processing question {response.get('question_id')}: {str(e)}")
                    raise

            # Update user level
            user_level = UserLevel.query.filter_by(
                user_id=user_id,
                subject=subject,
                level=int(level)
            ).first()

            if user_level:
                if float(score) > user_level.score:
                    user_level.score = float(score)
                user_level.updated_at = datetime.utcnow()
            else:
                user_level = UserLevel(
                    user_id=user_id,
                    level=int(level),
                    subject=subject,
                    score=float(score)
                )
                db.session.add(user_level)

            db.session.commit()
            
            return jsonify({
                "message": "Quiz submitted successfully",
                "score": score,
                "level": level
            })

        except Exception as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")
            return jsonify({
                "error": "Database error",
                "details": str(e)
            }), 500

    except Exception as e:
        print(f"Error in submit_level: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            "error": "Server error",
            "details": str(e)
        }), 500

# Track User Progress
@app.route('/progress/<subject>')
@login_required
def progress(subject):
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    levels = UserLevel.query.filter_by(user_id=user_id, subject=subject).all()
    
    total_score = sum(l.score for l in levels)      # Sum of all scores across levels
    total_possible_score = len(levels) * 20          # Maximum possible (20 points per level: 10 questions x 2 marks)
    average_percentage = (total_score / total_possible_score * 100) if total_possible_score > 0 else 0

    return jsonify({
        "levels": [{"level": l.level, "score": l.score} for l in levels],
        "average_score": round(average_percentage, 2),
        "average_score_raw": sum(l.score for l in levels) / len(levels) if levels else 0
    }), 200

@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('login'))

    # Calculate total quizzes across all subjects
    total_quizzes = QuizAttempt.query.filter_by(user_id=user_id).count()
    
    # Calculate achievements (completed levels with score > 80%)
    achievements = UserLevel.query.filter_by(
        user_id=user_id
    ).filter(UserLevel.score >= 8).count()  # Assuming 8 out of 10 is 80%
    
    # Calculate study streak
    recent_attempts = QuizAttempt.query.filter_by(
        user_id=user_id
    ).order_by(QuizAttempt.created_at.desc()).all()
    
    # Simple streak calculation - consecutive days with attempts
    streak = 0
    if recent_attempts:
        current_date = recent_attempts[0].created_at.date()
        for attempt in recent_attempts:
            if attempt.created_at.date() == current_date:
                continue
            elif attempt.created_at.date() == current_date - timedelta(days=1):
                streak += 1
                current_date = attempt.created_at.date()
            else:
                break
    
    # Calculate overall level based on average scores (percentage-based)
    user_levels = UserLevel.query.filter_by(user_id=user_id).all()
    overall_percentage = 0
    if user_levels:
        total_score = sum(level.score for level in user_levels)
        total_possible = len(user_levels) * 10  # Assuming max score is 10 per level
        overall_percentage = (total_score / total_possible) * 100
    
    # Map percentage to level (1-10)
    overall_level = max(1, min(10, int(overall_percentage / 10)))
    
    # Create user_data dictionary
    user_data = {
        'name': user.username,
        'level': overall_level,
        'total_quizzes': total_quizzes,
        'achievements': achievements,
        'study_streak': streak,
        'avatar': user.avatar if hasattr(user, 'avatar') else 'avatar1.jpg'
    }

    # Get progress for each subject
    subjects_data = {}
    for subject in ['math', 'physics', 'chemistry', 'english', 'computer', 'environment']:
        levels = UserLevel.query.filter_by(
            user_id=user_id,
            subject=subject
        ).order_by(UserLevel.level).all()
        
        # Calculate percentage-based average score
        avg_percentage = 0
        if levels:
            total_score = sum(level.score for level in levels)
            total_possible = len(levels) * 10  # Assuming max is 10 per level
            avg_percentage = (total_score / total_possible) * 100
        
        recent_attempts = QuizAttempt.query.filter_by(
            user_id=user_id,
            subject=subject
        ).order_by(QuizAttempt.created_at.desc()).limit(5).all()
        
        subjects_data[subject] = {
            'levels': [{'level': level.level, 'score': level.score} for level in levels],
            'average_score': round(avg_percentage, 1),  # Now percentage-based
            'recent_attempts': [{
                'date': attempt.created_at,
                'score': attempt.score
            } for attempt in recent_attempts]
        }

    return render_template(
        'profile.html',
        user=user_data,
        subjects_data=subjects_data,
        subjects={
            'math': {
                'name': 'Mathematics',
                'icon': 'fa-square-root-alt'
            },
            'physics': {
                'name': 'Physics',
                'icon': 'fa-atom'
            },
            'chemistry': {
                'name': 'Chemistry',
                'icon': 'fa-flask'
            },
            'english': {
                'name': 'English',
                'icon': 'fa-book'
            },
            'computer': {
                'name': 'Computer Practices',
                'icon': 'fa-desktop'
            },
            'environment': {
                'name': 'Environmental Science',
                'icon': 'fa-leaf'
            }
        }   
    )

@app.route('/update-avatar', methods=['POST'])
@login_required
def update_avatar():
    try:
        data = request.get_json()
        if not data or 'avatar' not in data:
            return jsonify({'success': False, 'error': 'Invalid request data'}), 400

        user = current_user
        user.avatar = data['avatar']
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"Error updating avatar: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_user_level_attempt(user_id: int, subject: str, level: int) -> Optional[Dict[str, Any]]:
    attempt = QuizAttempt.query.filter_by(
        user_id=user_id,
        subject=subject,
        question_id=level
    ).order_by(QuizAttempt.created_at.desc()).first()
    
    if not attempt:
        return None
    
    question_attempts = QuestionAttempt.query.filter_by(
        quiz_attempt_id=attempt.id
    ).all()
    
    if not question_attempts:
        return None
    
    QuestionModel = QUESTION_MODELS.get(subject.lower())

    attempt_data = {
        'attempt_date': attempt.created_at.strftime('%B %d, %Y %I:%M %p'),
        'score': attempt.score,
        'questions': []
    }
    
    for q_attempt in question_attempts:
        if QuestionModel:
            question = QuestionModel.query.get(q_attempt.question_id)
            if question:
                question_data = {
                    'text': question.question,
                    'options': q_attempt.options,  # Now directly using the stored options array
                    'selected': q_attempt.selected,  # Using the stored selected answer
                    'correct_answer': question.correct,
                    'is_correct': q_attempt.is_correct,
                    'explanation': question.solution
                }
                attempt_data['questions'].append(question_data)

    return attempt_data

@app.route('/level-details/<subject>/<int:level>')
@login_required
def level_details(subject, level):
    user_id = session.get('user_id')
    
    if not user_id:
        flash('User not authenticated')
        return redirect(url_for('login'))
    
    attempt_data = get_user_level_attempt(user_id, subject, level)
    
    # Add debug print
    print("Attempt data:", attempt_data)
    
    if not attempt_data:
        flash('No attempt found for this level')
        return redirect(url_for('profile'))
    
    return render_template('level-details.html',
                         subject=subject.capitalize(),
                         level=level,
                         attempt_date=attempt_data['attempt_date'],
                         score=attempt_data['score'],
                         questions=attempt_data['questions'])

@app.route('/debug-session')
def debug_session():
    """Debug endpoint to check session state and user existence"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                "error": "No user_id in session",
                "session_data": dict(session)
            })

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({
                "error": "User not found in database",
                "user_id": user_id,
                "session_data": dict(session)
            })

        return jsonify({
            "user_id": user_id,
            "username": user.username,
            "email": user.email,
            "session_data": dict(session)
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "session_data": dict(session) if 'session' in globals() else "No session"
        })

@app.route('/download-certificate/<subject>')
@login_required
def download_certificate(subject):
    """Handle certificate download as PNG"""
    # This route doesn't need to do any server-side processing
    # The actual screenshot and download will be handled by client-side JavaScript
    return redirect(url_for('generate_certificate', subject=subject))

@app.route('/certificate/<subject>')
@login_required
def generate_certificate(subject):
    """Generate a certificate for a specific subject"""
    subject = subject.lower()  # Ensure subject is in lowercase to match AVAILABLE_SUBJECTS keys
    if subject not in AVAILABLE_SUBJECTS:
        flash('Invalid subject selected', 'danger')
        return redirect(url_for('profile'))
        
    # Get user data
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))
    
    # Check if user has completed the course for this subject
    user_level = UserLevel.query.filter_by(
        user_id=user_id, 
        subject=subject
    ).order_by(UserLevel.level.desc()).first()
    
    # # Define the minimum level required to earn a certificate (can be adjusted)
    # MIN_LEVEL_FOR_CERTIFICATE = 50
    
    # if not user_level or user_level.level < MIN_LEVEL_FOR_CERTIFICATE:
    #     flash(f'You need to complete at least {MIN_LEVEL_FOR_CERTIFICATE} levels in {AVAILABLE_SUBJECTS[subject]["name"]} to earn a certificate', 'warning')
    #     return redirect(url_for('profile'))
    
    # Get subject statistics
    subject_stats = get_subject_stats(user.id, subject)
    
    # Set subject-specific colors and titles
    subject_colors = {
        'math': {'primary': '#6366F1', 'secondary': '#10B981', 'accent': '#F43F5E'},
        'physics': {'primary': '#8B5CF6', 'secondary': '#EC4899', 'accent': '#F59E0B'},
        'chemistry': {'primary': '#10B981', 'secondary': '#3B82F6', 'accent': '#F59E0B'},
        'english': {'primary': '#3B82F6', 'secondary': '#8B5CF6', 'accent': '#10B981'},
        'computer': {'primary': '#F97316', 'secondary': '#6366F1', 'accent': '#10B981'},
        'environment': {'primary': '#10B981', 'secondary': '#3B82F6', 'accent': '#F97316'}
    }
    
    # Certificate context with all required data
    certificate_data = {
        'username': user.username,
        'subject_name': AVAILABLE_SUBJECTS[subject]['name'],
        'level_completed': user_level.level,
        'starting_date': subject_stats['first_attempt_date'].strftime('%b %d, %Y') if subject_stats['first_attempt_date'] else 'N/A',
        'completion_date': subject_stats['last_attempt_date'].strftime('%b %d, %Y') if subject_stats['last_attempt_date'] else 'N/A',
        'time_invested': f"{subject_stats['hours_spent']} Hours",
        'average_score': f"{subject_stats['average_score']}%",
        'colors': subject_colors.get(subject, subject_colors['math'])  # Default to math colors if subject not found
    }
    
    return render_template('CERTIFICATE.html', **certificate_data)

def get_subject_stats(user_id, subject):
    """Calculate statistics for a user's performance in a specific subject"""
    # Get all attempts for this subject
    attempts = QuizAttempt.query.filter_by(
        user_id=user_id,
        subject=subject
    ).order_by(QuizAttempt.created_at).all()
    
    if not attempts:
        return {
            'first_attempt_date': None,
            'last_attempt_date': None,
            'hours_spent': 0,
            'average_score': 0
        }
    
    # Calculate statistics
    first_attempt = attempts[0].created_at
    last_attempt = attempts[-1].created_at
    
    # Estimate hours spent (assume 10 minutes per attempt)
    hours_spent = round(len(attempts) * 10 / 60, 1)
    
    # Calculate average score
    total_score = sum(attempt.score for attempt in attempts)
    total_possible_score = len(attempts) * 10    # Assuming each attempt has a maximum score of 10
    average_score = round((total_score / total_possible_score) * 100, 1) if total_possible_score > 0 else 0
    
    return {
        'first_attempt_date': first_attempt,
        'last_attempt_date': last_attempt,
        'hours_spent': hours_spent,
        'average_score': average_score
    }
    
# Reset Progress
@app.route('/reset-progress', methods=['POST'])
@login_required
def reset_progress():
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        subject = data.get('subject')
        
        # Delete only the records for the specified subject
        UserLevel.query.filter_by(
            user_id=user_id,
            subject=subject
        ).delete()
        
        db.session.commit()
        return jsonify({
            "message": f"{subject.capitalize()} progress reset successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"Failed to reset progress: {str(e)}"
        }), 500

@app.route('/test-email')
def test_email():
    try:
        msg = Message(
            'Test Email',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=['your-test-email@example.com']
        )
        msg.body = 'This is a test email from your Flask application.'
        mail.send(msg)
        return 'Email sent successfully!'
    except Exception as e:
        return f'Error sending email: {str(e)}'

def test_email_config():
    try:
        with app.app_context():
            msg = Message(
                subject='Test Email',
                recipients=[os.getenv('MAIL_USERNAME')],  # Send test email to yourself
                body='This is a test email to verify SMTP configuration.'
            )
            mail.send(msg)
            return True
    except Exception as e:
        print(f"Email configuration error: {str(e)}")
        return False

mail = Mail()

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            
            user = User.query.filter_by(email=email).first()
            if user:
                # Generate a secure token
                token = secrets.token_urlsafe(32)
                
                # Create a new password reset request with UTC timezone
                now = datetime.now(timezone.utc)
                reset_request = PasswordReset(
                    user_id=user.id,
                    token=token,
                    created_at=now,
                    expires_at=now + timedelta(hours=1)
                )
                
                try:
                    # Delete any existing unused tokens for this user
                    PasswordReset.query.filter_by(
                        user_id=user.id,
                        used=False
                    ).delete()
                    
                    # Add new reset request
                    db.session.add(reset_request)
                    db.session.commit()
                    
                    # Generate reset URL
                    reset_url = url_for('reset_password', token=token, _external=True)
                    
                    # Send email
                    msg = Message(
                        'Password Reset Request',
                        recipients=[user.email],
                        html=render_template(
                            'email/reset_password.html',
                            user=user,
                            reset_url=reset_url
                        )
                    )
                    mail.send(msg)
                    print(f"Reset email sent to {user.email} with URL: {reset_url}")
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"Error creating reset token: {str(e)}")
                    raise
            
            flash('If an account exists with that email, you will receive password reset instructions.', 'info')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Password reset error: {str(e)}")
            flash('An error occurred. Please try again later.', 'error')
    
    return render_template('forgot_password.html')

@app.route('/debug/check-reset-tokens')
def check_reset_tokens():
    try:
        # Get all tokens from the last 24 hours
        recent_tokens = PasswordReset.query.filter(
            PasswordReset.created_at >= datetime.now(timezone.utc) - timedelta(days=1)
        ).all()
        
        tokens_info = []
        for token in recent_tokens:
            tokens_info.append({
                'token': token.token,
                'user_id': token.user_id,
                'created_at': token.created_at.isoformat(),
                'expires_at': token.expires_at.isoformat(),
                'used': token.used
            })
        
        return jsonify({
            'count': len(tokens_info),
            'tokens': tokens_info
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        })

@app.route('/check-token/<token>')
def check_token(token):
    try:
        reset_request = PasswordReset.query.filter_by(token=token).first()
        
        if reset_request:
            return jsonify({
                'exists': True,
                'used': reset_request.used,
                'expires_at': reset_request.expires_at.isoformat(),
                'current_time': datetime.now(timezone.utc).isoformat(),
                'is_expired': reset_request.expires_at < datetime.now(timezone.utc)
            })
        else:
            return jsonify({
                'exists': False,
                'error': 'Token not found in database'
            })
    except Exception as e:
        return jsonify({
            'error': str(e)
        })

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not token:
        flash('Invalid reset link.', 'error')
        return redirect(url_for('login'))
    
    # Find the reset request
    reset_request = PasswordReset.query.filter_by(
        token=token,
        used=False
    ).first()
    
    if not reset_request:
        flash('Invalid or expired reset link.', 'error')
        return redirect(url_for('login'))
    
    # Convert stored expires_at to UTC if it's naive
    expires_at = reset_request.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    # Check if token is expired
    now = datetime.now(timezone.utc)
    if expires_at < now:
        flash('This reset link has expired. Please request a new one.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        try:
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not password or not confirm_password:
                flash('Please fill in all fields.', 'error')
                return redirect(url_for('reset_password', token=token))
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return redirect(url_for('reset_password', token=token))
            
            # Update the user's password
            user = User.query.get(reset_request.user_id)
            if not user:
                flash('User not found.', 'error')
                return redirect(url_for('login'))
            
            user.password = generate_password_hash(password)
            reset_request.used = True
            db.session.commit()
            
            flash('Your password has been updated successfully. Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error resetting password: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('reset_password.html', token=token)

@app.route('/debug/check-token/<token>')
def debug_check_token(token):
    reset_request = PasswordReset.query.filter_by(token=token).first()
    if reset_request:
        now = datetime.now(timezone.utc)
        expires_at = reset_request.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            
        return jsonify({
            'exists': True,
            'user_id': reset_request.user_id,
            'created_at': reset_request.created_at.isoformat(),
            'expires_at': expires_at.isoformat(),
            'current_time': now.isoformat(),
            'used': reset_request.used,
            'expired': expires_at < now
        })
    return jsonify({'exists': False})

@app.route('/debug/mail-config')
def debug_mail_config():
    return jsonify({
        'MAIL_SERVER': app.config.get('MAIL_SERVER'),
        'MAIL_PORT': app.config.get('MAIL_PORT'),
        'MAIL_USE_TLS': app.config.get('MAIL_USE_TLS'),
        'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
        'MAIL_DEFAULT_SENDER': app.config.get('MAIL_DEFAULT_SENDER')
    })

try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")

init_app()

if __name__ == '__main__':
    app.run(debug=True)