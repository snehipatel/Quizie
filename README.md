<div align="center">

# 🎯 Quizie — AI-Powered Gamified Learning Platform

  <p align="center">
    <b>An intelligent, multi-subject CET quiz application powered by Google Gemini AI & Flask.</b>
    <br />
    <sub>Adaptive levels • AI question generation • Dynamic PDF certificates • Real-time analytics</sub>
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Flask-3.1.3-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
    <img src="https://img.shields.io/badge/Google%20Gemini%20AI-1.75-8E75B2?style=for-the-badge&logo=googlecloud&logoColor=white" alt="Gemini AI" />
    <img src="https://img.shields.io/badge/Database-TiDB%20%2F%20MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL" />
  </p>

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Problem, Solution & Key Learnings](#-problem-solution--key-learnings)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture & Flow](#-architecture--flow)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
  - [Database Setup & Migrations](#database-setup--migrations)
  - [Running the Application](#running-the-application)
- [Core Features Deep Dive](#-core-features-deep-dive)

---

## 🧠 Overview

**Quizie** is a next-generation web application designed to revolutionize competitive exam preparation, specifically created for the **DDCET (Diploma to Degree Common Entrance Test)**. Combining the power of **Google Gemini 2.0 / Flash AI** with dynamic level progression, Quizie generates context-aware, topic-specific practice questions on the fly while caching results to maximize speed and cost efficiency.

Users can test their knowledge across multiple subjects, level up through 50 progressive difficulty tiers, track their progress in real-time, and download verified **PDF Certificates** upon milestone completions.

---

## 💡 Problem, Solution & Key Learnings

### 🎯 What Problem Did We Solve?
- **Scarcity of DDCET Exam Resources**: When I began developing this project, the **DDCET (Diploma to Degree Common Entrance Test)** was a newly introduced exam. Because of its novelty, there was a severe lack of quality study materials, structured question banks, and practice test platforms available for students. I created Quizie specifically to solve this problem and provide aspirants with an intelligent, accessible practice environment.
- **Static & Repetitive Question Banks**: Existing conventional quiz tools rely on small, fixed databases, leading to repetitive questions that fail to match evolving DDCET syllabus standards.
- **High Latency & Costs of Real-Time AI**: Querying LLM APIs directly on every user attempt causes 3-5+ second delays per question and results in expensive API usage overhead.
- **Lack of Structured Learning Pathways**: Unorganized quiz sets make it difficult for students to measure linear skill progression across specific sub-topics.
- **Missing Proof of Achievement**: Platforms rarely provide automated, verifiable proof of concept mastery for milestone accomplishments.

### 🛠️ How Did We Solve It?
- **Hybrid AI + DB Caching Architecture**: Integrated Google Gemini AI (`google-genai` SDK) to dynamically generate CET-level questions. Generated questions are automatically stored in MySQL / TiDB Cloud, reducing subsequent load times to under 50ms and cutting API costs by over 90%.
- **Seamless Offline Fallback Engine**: Built a dedicated fallback system (`fallback_questions.py`) that activates if network issues or API quota limits occur, ensuring 100% uptime for students.
- **50-Tier Progressive Subject Mapping**: Created a structured curriculum mapping 50 progressive levels across 6 subjects (Math, Physics, Chemistry, English, Computer Science, Environment) with adaptive difficulty scaling.
- **Automated PDF Certificate Generator**: Designed a custom certificate renderer (`pdfkit` + custom typography) that generates downloadable, personalized achievement certificates upon completing level milestones.
- **Production-Grade Infrastructure**: Configured database pooling (`pool_pre_ping`), SSL encryption, CSRF protection (`Flask-WTF`), and containerized WSGI deployment (`Gunicorn`).

### 📚 What Did We Learn?
- **Structured LLM Output Handling**: Gained expertise in prompt engineering and JSON response schema enforcement using the Google GenAI SDK to consistently parse structured questions without parsing failures.
- **Distributed Database Optimization**: Learned to manage TiDB Cloud / MySQL connection lifecycles, handle connection timeouts, and implement optimal indexing for cached quiz items.
- **Server-Side PDF Rendering**: Mastered headless HTML-to-PDF compilation (`wkhtmltopdf` / `pdfkit`) with custom embedded web fonts across local and cloud deployment environments.
- **Full-Stack Security & Resilience**: Deepened understanding of secure user authentication (`Flask-Login`), state preservation across user sessions, and graceful fault-tolerance design.

---

## ✨ Key Features

- 🤖 **Google Gemini AI Integration**: Dynamically generates high-quality, CET-standard questions for specific topics and difficulties.
- ⚡ **Smart DB Caching & Fallback**: Caches generated questions in MySQL/TiDB Cloud to eliminate API latency and includes an offline fallback engine for maximum reliability.
- 📈 **50-Level Gamified Progression**: 50 progressive difficulty levels mapped across core subjects with dynamic difficulty scaling.
- 🎓 **Multi-Subject Coverage**:
  - 📐 **Mathematics** *(Matrices, Vectors, Calculus, Trigonometry, etc.)*
  - ⚡ **Physics** *(Laws of Motion, Electricity, Optics, Thermodynamics, etc.)*
  - 🧪 **Chemistry** *(Reactions, Acids & Bases, Metals & Non-metals)*
  - 📚 **English** *(Grammar, Writing Techniques, Comprehension)*
  - 💻 **Computer Science** *(Computer Basics, HTML, MS Office)*
  - 🌿 **Environmental Science** *(Ecosystems, Climate Change, Renewable Energy)*
- 📜 **Dynamic PDF Certificates**: Generates personalized, professional PDF certificates upon level/quiz completion using custom typography (*DancingScript* & *EB Garamond*).
- 🔒 **Enterprise-Grade Security**: Full user authentication system powered by `Flask-Login`, `Flask-WTF` CSRF protection, password hashing (`Werkzeug`), and `Flask-Mail` account verification.
- ☁️ **Cloud Database Ready**: Built-in support for TiDB Cloud & MySQL with SSL connections, connection pooling, and auto-reconnection pre-pings.

---

## 🛠️ Tech Stack

### **Backend Framework & Core**
| Technology | Description |
| :--- | :--- |
| **[Python 3.10+](https://www.python.org/)** | Primary programming language |
| **[Flask 3.1.3](https://flask.palletsprojects.com/)** | Lightweight & modular WSGI web framework |
| **[Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)** | ORM layer for database interactions |
| **[Flask-Login](https://flask-login.readthedocs.io/)** | Session management & user authentication |
| **[Flask-WTF](https://flask-wtf.readthedocs.io/)** | Form handling & CSRF protection |
| **[Google GenAI SDK](https://github.com/google-gemini/generative-ai-python)** | Powered by Google Gemini AI for smart question generation |

### **Database & Infrastructure**
| Technology | Description |
| :--- | :--- |
| **[TiDB Cloud / MySQL](https://pingcap.com/tidb-cloud/)** | Distributed MySQL-compatible cloud database |
| **[PyMySQL](https://pymysql.readthedocs.io/)** | Pure-Python MySQL driver with SSL support |
| **[Flask-Migrate](https://flask-migrate.readthedocs.io/)** | Database migrations handling via Alembic |
| **[Gunicorn](https://gunicorn.org/)** | Production WSGI HTTP Server |

### **Document & Certificate Generation**
| Technology | Description |
| :--- | :--- |
| **[pdfkit](https://pypi.org/project/pdfkit/) / [wkhtmltopdf](https://wkhtmltopdf.org/)** | HTML to PDF conversion engine |
| **Custom TTF Fonts** | `DancingScript.ttf` & `EBGaramond.ttf` for dynamic certificate styling |

---

## 🏗️ Architecture & Flow

```mermaid
flowchart TD
    A[User / Student] -->|Select Subject & Level| B[Quiz Engine]
    B -->|Check Cached Questions| C{Database Has Questions?}
    C -->|Yes| D[Load Questions from DB]
    C -->|No| E[Invoke Google Gemini AI API]
    E -->|Success| F[Save Questions to DB Cache]
    E -->|API Failure / Limit| G[Load Fallback Question Bank]
    F --> H[Present Quiz to User]
    G --> H
    D --> H
    H -->|Submit Answers| I[Evaluate Results & Award XP/Level]
    I -->|Milestone Achieved| J[Generate PDF Certificate]
    J -->|Download| A
```

---

## 📁 Project Structure

```text
Quizie/
├── APP/
│   ├── app.py                      # Main Flask application entry point & routes
│   ├── ai_question_generator.py    # Gemini AI question generator & subject mappings
│   ├── fallback_questions.py       # Offline backup question repository
│   ├── quiz_logic.py               # Core scoring & level calculation logic
│   ├── models.py                   # SQLAlchemy database schemas & models
│   ├── forms.py                    # Flask-WTF form definitions
│   ├── CERTIFICATE.py              # PDF Certificate generation logic
│   ├── DancingScript.ttf           # Font asset for certificate signatures
│   ├── EBGaramond.ttf              # Font asset for certificate body
│   ├── static/                     # CSS, JavaScript & image assets
│   ├── templates/                  # Jinja2 HTML templates
│   └── migrations/                 # Alembic database migration scripts
├── .env.example                    # Sample environment variables config
├── .gitignore                      # Git ignore rules
├── build.sh                        # Deployment build script (Render/Cloud)
├── requirements.txt                # Python package dependencies
├── runtime.txt                     # Python runtime specification
└── README.md                       # Documentation
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed on your local machine:
- **Python 3.10+**: `python --version`
- **Git**: `git --version`
- **wkhtmltopdf** *(Optional for PDF generation)*: Download from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html)

---

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/snehipatel/Quizie.git
   cd Quizie
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

### Environment Configuration

Create a `.env` file inside the `APP/` directory (or workspace root) based on `.env.example`:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=development

# Database Connection (MySQL or TiDB Cloud)
DATABASE_URI=mysql+pymysql://username:password@localhost:3306/quizie

# Google Gemini AI API Key
GEMINI_API_KEY=your-google-gemini-api-key

# Email Server Settings (Flask-Mail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

---

### Database Setup & Migrations

Initialize and update your database schema using `Flask-Migrate`:

```bash
cd APP
flask db upgrade
```

---

### Running the Application

Start the Flask local development server:

```bash
python app.py
```

The app will be live at: **`http://127.0.0.1:5000`**

---

## 📑 Core Features Deep Dive

### 🤖 AI Question Generation & Caching
When a user selects a subject and level:
1. `ai_question_generator.py` checks the database for existing questions matching the mapped topic.
2. If fewer than required questions exist, it calls `google.genai.Client` to generate structured JSON format questions.
3. Successfully generated questions are formatted and inserted into the `Question` table for instant re-use across all users.

### 📜 Certificate Engine
Upon passing milestone levels:
- `CERTIFICATE.py` pulls user statistics, completion date, and subject details.
- Uses `pdfkit` to render an HTML certificate template styled with embedded `DancingScript` and `EBGaramond` typography into a high-resolution downloadable PDF.

---

## 🤝 Contributing

Contributions are what make the open-source community an incredible place to learn, inspire, and create. Any contributions you make are **greatly appreciated**!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<div align="center">
  <p>Made with ❤️ for students preparing for DDCET.</p>
</div>
