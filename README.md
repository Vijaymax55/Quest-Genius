# Quest Genius

An AI-powered NCERT learning platform that helps Class 8–10 students with topic summaries, AI-generated question papers, and automated assessment evaluation.

## Features

- **Topic Summarizer** — Generates structured, easy-to-understand summaries for any NCERT chapter and topic
- **AI Chatbot** — Answers student questions based on NCERT content
- **Assessment Generator** — Creates question papers with MCQs, fill-in-the-blanks, and short answer questions
- **Auto Evaluation** — Evaluates handwritten answer sheets uploaded as images using OCR and GPT feedback
- **PDF Export** — Download question papers and answer keys as PDFs

## Tech Stack

- **Backend:** Python 3.12, Flask
- **AI:** OpenAI GPT-4o-mini
- **OCR:** Tesseract (pytesseract)
- **PDF Generation:** fpdf2
- **Frontend:** HTML, CSS, JavaScript
- **Tooling:** [uv](https://docs.astral.sh/uv/) for Python and dependency management

## Project Structure

```
Quest-Genius/
├── app.py                      # Main Flask application
├── config.py                   # Loads .env and validates settings
├── api_routes.py               # Summary & chatbot API routes
├── api_assessment_routes.py    # Question generation & PDF routes
├── api_evaluation_routes.py    # Assessment evaluation routes
├── fine_tunning.py             # Script to prepare fine-tuning data
├── fine_tuning_data.jsonl      # NCERT training data (JSONL)
├── learning_materials/         # NCERT PDFs (Class 8, 9, 10)
├── answerkey/                  # Generated papers & answer keys (runtime, not tracked)
├── templates/                  # HTML templates
├── static/                     # CSS, JS, images
├── pyproject.toml / uv.lock    # Dependencies
└── .env.example                # Environment variable template
```

## Prerequisites

- **uv** — installs Python 3.12 and all Python packages for you:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Tesseract OCR** — a system program used to read handwritten answer sheets. It is **not** a Python package, so `uv sync` does not install it:
  ```bash
  # macOS
  brew install tesseract

  # Ubuntu / Debian
  sudo apt install tesseract-ocr
  ```
- **An OpenAI API key** — from https://platform.openai.com/api-keys

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Vijaymax55/Quest-Genius.git
cd Quest-Genius
```

### 2. Install dependencies

```bash
uv sync
```

This creates a `.venv/` with Python 3.12 and every dependency pinned in `uv.lock`.

### 3. Create your `.env`

```bash
cp .env.example .env
```

Then edit `.env`:

| Variable         | Required | Description                                                                 |
|------------------|----------|-----------------------------------------------------------------------------|
| `OPENAI_API_KEY` | Yes      | Your OpenAI API key. The app refuses to start without it.                   |
| `SECRET_KEY`     | No       | Flask session signing key. Falls back to an insecure dev-only default.      |
| `FLASK_DEBUG`    | No       | `true` enables the debugger and auto-reload. Defaults to `false`.           |

Generate a `SECRET_KEY` with:

```bash
uv run python -c "import secrets; print(secrets.token_hex(32))"
```

`.env` is git-ignored — never commit it.

### 4. Run the app

```bash
uv run python app.py
```

Open your browser at `http://localhost:5050`

## Usage

1. Select a subject (Physics, Chemistry, Biology)
2. Enter your class, chapter, and topic to get a summary
3. Generate a question paper for assessment
4. Upload handwritten answer sheet images (3 images) for auto-evaluation
5. Download question paper and answer key PDFs

## Notes

- The `answerkey/` folder stores generated question papers and answer keys locally and is not tracked in git
- Learning materials are NCERT PDFs for Class 8, 9, and 10
- Fine-tuning data is generated from learning materials using `uv run python fine_tunning.py`
