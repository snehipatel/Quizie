"""
AI Question Generator for Quizie
Uses Google Gemini API (google-genai SDK) to generate CET-level quiz questions.
Questions are cached in the database to avoid redundant API calls.
"""

import os
import json
import random
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini client
_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# ── Subject -> Topic lists (must match DB Enum values exactly)
SUBJECT_TOPICS = {
    'math': [
        'Matrices', 'Determinant', 'Function', 'Limit', 'Logarithm',
        'Trigonometry', 'Vectors', 'Coordinate Geometry',
        'Differentiation', 'Integration'
    ],
    'physics': [
        'Units and measurements', 'Heat and thermometry', 'Laws of Motion',
        'work and energy', 'Electric current', 'Wave option, optics and acoustics'
    ],
    'chemistry': [
        'Chemical reactions and equations', 'Acid, Base and Salts',
        'Metals and Non-metals'
    ],
    'english': [
        'Comprehension of Unseen Passage', 'Theory of Communication',
        'Techniques of Writing', 'Grammar',
        'Correction of incorrect words and sentences'
    ],
    'computer': [
        'Basics of Computer System', 'Introduction to Internet HTML',
        'MS-Word', ' MS-Excel', ' MS-Power Point'
    ],
    'environment': [
        'Ecosystem', 'Pollution and its types', 'Climate Change',
        'Renewable Energy'
    ]
}

# ── 50-level topic map per subject
def build_level_topic_map(topics: list, total_levels: int = 50) -> dict:
    mapping = {}
    for level in range(1, total_levels + 1):
        topic_index = (level - 1) % len(topics)
        mapping[level] = topics[topic_index]
    return mapping

LEVEL_TOPIC_MAP = {
    subject: build_level_topic_map(topics)
    for subject, topics in SUBJECT_TOPICS.items()
}

DIFFICULTIES = ['Easy', 'Medium', 'Hard']

# Models to try in order (fallback chain)
MODELS_TO_TRY = ['gemini-2.0-flash-lite', 'gemini-2.0-flash', 'gemini-1.5-flash-latest']


def _build_prompt(subject: str, topic: str, difficulty: str, count: int) -> str:
    subject_context = {
        'math': 'Mathematics (Diploma to Degree level)',
        'physics': 'Physics (Diploma to Degree level)',
        'chemistry': 'Chemistry (Diploma to Degree level)',
        'english': 'English language and communication',
        'computer': 'Computer Applications and Fundamentals',
        'environment': 'Environmental Science'
    }.get(subject, subject)

    difficulty_guidance = {
        'Easy': 'focus on basic definitions, simple recall, and straightforward single-step problems',
        'Medium': 'include moderate calculations, conceptual application, and two-step reasoning',
        'Hard': 'include advanced multi-step problem-solving, complex applications, and deep conceptual understanding'
    }.get(difficulty, 'moderate difficulty')

    return f"""You are an expert question paper setter for the Indian Diploma-to-Degree Common Entrance Test (CET).

Generate exactly {count} multiple-choice questions for:
- Subject: {subject_context}
- Topic: {topic}
- Difficulty Level: {difficulty} ({difficulty_guidance})

STRICT REQUIREMENTS:
1. Each question must be appropriate for Diploma-to-Degree CET level students in India.
2. Each question must have exactly 1 correct answer and 3 plausible but clearly wrong options.
3. The solution/explanation must be clear, step-by-step where applicable, and educational.
4. Do NOT repeat questions. Make them unique and varied.
5. Questions must test conceptual understanding relevant to the CET exam pattern.

Respond ONLY with a valid JSON array. No extra text, no markdown, no code blocks. Just raw JSON.

Format:
[
  {{
    "question": "Full question text here?",
    "correct": "The correct answer",
    "incorrect1": "First wrong option",
    "incorrect2": "Second wrong option",
    "incorrect3": "Third wrong option",
    "solution": "Step-by-step explanation of why the correct answer is right.",
    "difficulty_level": "{difficulty}",
    "topic_name": "{topic}"
  }}
]"""


def generate_questions_from_ai(subject: str, topic: str, difficulty: str, count: int = 5) -> list:
    """
    Call Gemini API to generate questions. Retries on rate-limit errors.
    Tries multiple models as fallback.
    """
    prompt = _build_prompt(subject, topic, difficulty, count)

    for model_name in MODELS_TO_TRY:
        for attempt in range(3):
            try:
                print(f"[AI Generator] Attempt {attempt+1} with model '{model_name}'...")
                response = _client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.8,
                        max_output_tokens=8192,
                    )
                )

                raw_text = response.text.strip()

                # Strip markdown code fences if present
                if raw_text.startswith('```'):
                    lines = raw_text.split('\n')
                    lines = lines[1:] if lines[0].startswith('```') else lines
                    lines = lines[:-1] if lines[-1].strip() == '```' else lines
                    raw_text = '\n'.join(lines).strip()

                questions = json.loads(raw_text)

                required_fields = {'question', 'correct', 'incorrect1', 'incorrect2', 'incorrect3', 'solution'}
                validated = []
                for q in questions:
                    if isinstance(q, dict) and required_fields.issubset(q.keys()):
                        q['difficulty_level'] = difficulty
                        q['topic_name'] = topic
                        validated.append(q)

                print(f"[AI Generator] SUCCESS with {model_name}: {len(validated)} questions")
                return validated

            except Exception as e:
                error_str = str(e)
                print(f"[AI Generator] {model_name} attempt {attempt+1} error: {error_str[:200]}")

                if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                    print(f"[AI Generator] Quota exhausted for {model_name}, trying next model...")
                    break  # skip retries, try next model immediately
                elif '404' in error_str or 'NOT_FOUND' in error_str:
                    print(f"[AI Generator] {model_name} not available, trying next...")
                    break
                else:
                    import traceback
                    traceback.print_exc()
                    break

    # ALL models failed - use fallback questions
    print("[AI Generator] All AI models failed. Using fallback question bank.")
    from fallback_questions import get_fallback_questions
    return get_fallback_questions(subject, topic, count)


def get_topic_for_level(subject: str, level: int) -> str:
    return LEVEL_TOPIC_MAP.get(subject, {}).get(level, SUBJECT_TOPICS.get(subject, [''])[0])


def get_random_difficulty() -> str:
    return random.choice(DIFFICULTIES)
