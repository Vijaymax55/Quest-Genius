# Quest Genius

An AI-powered NCERT learning platform that helps Class 8–10 students with topic summaries, AI-generated question papers, and automated assessment evaluation.

## Features

- **Topic Summarizer** — Generates structured, easy-to-understand summaries for any NCERT chapter and topic
- **AI Chatbot** — Answers student questions based on NCERT content
- **Assessment Generator** — Creates question papers with MCQs, fill-in-the-blanks, and short answer questions
- **Auto Evaluation** — Evaluates handwritten answer sheets uploaded as images using OCR and GPT feedback
- **PDF Export** — Download question papers and answer keys as PDFs

## Tech Stack

- **Backend:** Python, Flask
- **AI:** OpenAI GPT-4o-mini
- **OCR:** Tesseract (pytesseract)
- **PDF Generation:** fpdf
- **Frontend:** HTML, CSS, JavaScript

## Project Structure

```
Quest-Genius/
├── app.py                      # Main Flask application
├── api_routes.py               # Summary & chatbot API routes
├── api_assessment_routes.py    # Question generation & PDF routes
├── api_evaluation_routes.py    # Assessment evaluation routes
├── fine_tunning.py             # Script to prepare fine-tuning data
├── fine_tuning_data.jsonl      # NCERT training data (JSONL)
├── learning_materials/         # NCERT PDFs (Class 8, 9, 10)
├── answerkey/                  # Generated question papers & answer keys
├── templates/                  # HTML templates
├── static/                     # CSS, JS, images
└── .env.example                # Environment variable template
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Vijaymax55/Quest-Genius.git
cd Quest-Genius
```

### 2. Install dependencies

```bash
pip install flask openai pillow pytesseract fuzzywuzzy fpdf pdfplumber
```

Also install Tesseract OCR:

```bash
# macOS
brew install tesseract

# Ubuntu
sudo apt install tesseract-ocr
```

### 3. Set your OpenAI API key

```bash
cp .env.example .env
```

Edit `.env` and add your key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Then export it before running:

```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the app

```bash
python app.py
```

Open your browser at `http://localhost:5000`

## Usage

1. Select a subject (Physics, Chemistry, Biology)
2. Enter your class, chapter, and topic to get a summary
3. Generate a question paper for assessment
4. Upload handwritten answer sheet images (3 images) for auto-evaluation
5. Download question paper and answer key PDFs

## Notes

- The `answerkey/` folder stores generated question papers and answer keys locally
- Learning materials are NCERT PDFs for Class 8, 9, and 10
- Fine-tuning data is generated from learning materials using `fine_tunning.py`
