from flask import Blueprint, request, jsonify
import openai
import json
import os
from flask import send_file
from fpdf import FPDF
import json
import unicodedata

# Define Blueprint for API Routes
api_assessment_routes = Blueprint("api_assessment_routes", __name__)

# OpenAI API Key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Fine-Tuned Model Details
FINE_TUNED_MODEL = "gpt-4o-mini"
FINE_TUNED_DATA_PATH = "fine_tuning_data.jsonl"

# ✅ Ensure Answer Key Directory Exists
ANSWER_KEY_DIR = "answerkey"
os.makedirs(ANSWER_KEY_DIR, exist_ok=True)

# ✅ Load Fine-Tuned NCERT Learning Material
def load_fine_tuned_data():
    """ Load fine-tuned NCERT data from JSONL file """
    knowledge_base = []
    if os.path.exists(FINE_TUNED_DATA_PATH):
        with open(FINE_TUNED_DATA_PATH, "r", encoding="utf-8") as file:
            for line in file:
                knowledge_base.append(json.loads(line))
        print("✅ Fine-tuned data loaded successfully.")
    else:
        print("⚠️ Warning: Fine-tuned JSONL file not found.")
    return knowledge_base

fine_tuned_data = load_fine_tuned_data()

# ✅ Initialize OpenAI Client
def initialize_client():
    return openai.OpenAI(api_key=OPENAI_API_KEY)

# ✅ Fetch Relevant NCERT Content
def get_relevant_content(class_name, subject, chapter, topic):
    """ Retrieve NCERT content from the fine-tuned dataset """
    for entry in fine_tuned_data:
        if all([
            class_name.lower() in entry["messages"][0]["content"].lower(),
            subject.lower() in entry["messages"][0]["content"].lower(),
            chapter.lower() in entry["messages"][0]["content"].lower(),
            topic.lower() in entry["messages"][0]["content"].lower()
        ]):
            return entry["messages"][1]["content"]
    return None  # No match found

# ✅ Generate Unique Paper ID
def generate_paper_id():
    """ Generate a unique numeric Paper ID by checking existing JSON files. """
    existing_files = [f for f in os.listdir(ANSWER_KEY_DIR) if f.endswith(".json")]
    if not existing_files:
        return 1  # Start with 1 if no previous papers exist
    existing_ids = [int(f.split(".")[0]) for f in existing_files if f.split(".")[0].isdigit()]
    return max(existing_ids) + 1 if existing_ids else 1

# ✅ Store Questions & Answers in JSON File
def save_questions_with_answers(class_name, subject, chapter, topic, questions):
    """ Save generated questions in JSON file with a unique Paper ID and store answers separately. """
    paper_id = generate_paper_id()

    # ✅ Store only questions (without answers) for display
    questions_display = {
        "paper_id": paper_id,
        "class_name": class_name,
        "subject": subject,
        "chapter": chapter,
        "topic": topic,
        "mcqs": [{"question": q["question"], "options": q["options"]} for q in questions["mcqs"]],
        "fill_in_the_blanks": [{"question": q["question"]} for q in questions["fill_in_the_blanks"]],
        "short_questions": [{"question": q["question"]} for q in questions["short_questions"]]
    }

    # ✅ Store answers separately (hidden from display)
    answers = {
        "paper_id": paper_id,
        "mcqs": [{"question": q["question"], "answer": q["answer"]} for q in questions["mcqs"]],
        "fill_in_the_blanks": [{"question": q["question"], "answer": q["answer"]} for q in questions["fill_in_the_blanks"]],
        "short_questions": [{"question": q["question"], "answer": q["answer"]} for q in questions["short_questions"]]
    }

    try:
        # ✅ Save the question paper
        question_file = os.path.join(ANSWER_KEY_DIR, f"{paper_id}.json")
        with open(question_file, "w", encoding="utf-8") as f:
            json.dump(questions_display, f, indent=4)

        # ✅ Save the answer key separately
        answer_file = os.path.join(ANSWER_KEY_DIR, f"{paper_id}_answers.json")
        with open(answer_file, "w", encoding="utf-8") as f:
            json.dump(answers, f, indent=4)

        print(f"✅ Paper ID {paper_id} saved at {question_file} (Questions)")
        print(f"✅ Answers saved at {answer_file}")

        return paper_id  # Return the unique Paper ID for display

    except Exception as e:
        print(f"❌ Error saving JSON files: {e}")
        return None

# ✅ Generate Questions Using OpenAI Fine-Tuned Model
def generate_questions(class_name, subject, chapter, topic):
    client = initialize_client()

    # Fetch Fine-Tuned Content
    knowledge_content = get_relevant_content(class_name, subject, chapter, topic)

    if not knowledge_content:
        print("🔍 No direct match in NCERT dataset. Querying OpenAI fine-tuned model...")
        knowledge_content = f"Generate questions for Class {class_name}, Subject: {subject}, Chapter: {chapter}, Topic: {topic}."

    prompt = f"""
    Generate structured NCERT-based question paper.

    **Class:** {class_name}
    **Subject:** {subject}
    **Chapter:** {chapter}
    **Topic:** {topic}

    --- **Learning Material** ---
    {knowledge_content}

    **Generate Questions:**
    - 5 MCQs (Each with 4 options and correct answer)
    - 5 Fill in the blanks (with answers)
    - 5 Short answer questions (1-2 lines)

    **Response Format (Must be JSON):**
    {{
        "mcqs": [{{"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "..."}}],
        "fill_in_the_blanks": [{{"question": "...", "answer": "..."}}],
        "short_questions": [{{"question": "...", "answer": "..."}}]
    }}
    """

    try:
        response = client.chat.completions.create(
            model=FINE_TUNED_MODEL,
            messages=[{"role": "system", "content": "You generate NCERT-based question papers."},
                        {"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )

        return json.loads(response.choices[0].message.content.strip())

    except Exception as e:
        print(f"❌ Error generating questions: {e}")
        return None

# ✅ API Endpoint: Generate Questions & Display on Screen
@api_assessment_routes.route('/api/generate_assessment', methods=['POST'])
def generate_questions_api():
    """ API Endpoint to generate assessment questions and return only the question paper. """
    try:
        data = request.json
        class_name, subject, chapter, topic = data.get("class_name"), data.get("subject"), data.get("chapter"), data.get("topic")

        if not all([class_name, subject, chapter, topic]):
            return jsonify({"error": "All fields (class, subject, chapter, topic) are required."}), 400

        questions = generate_questions(class_name, subject, chapter, topic)

        if questions:
            paper_id = save_questions_with_answers(class_name, subject, chapter, topic, questions)

            if paper_id is None:
                return jsonify({"error": "Failed to save questions. Try again."}), 500

            # ✅ Filter out answers before returning the response
            questions_without_answers = {
                "mcqs": [{"question": q["question"], "options": q["options"]} for q in questions["mcqs"]],
                "fill_in_the_blanks": [{"question": q["question"]} for q in questions["fill_in_the_blanks"]],
                "short_questions": [{"question": q["question"]} for q in questions["short_questions"]]
            }

            return jsonify({
                "paper_id": paper_id,  # ✅ Add paper_id here
                "questions": questions_without_answers  # ✅ Return only questions (without answers)
            })
        else:
            return jsonify({"error": "Failed to generate questions"}), 500

    except Exception as e:
        print(f"❌ Error in generate_questions_api: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500
    
# ✅ Convert JSON to PDF
def clean_text(text):
    """ Normalize and remove unsupported Unicode characters. """
    if isinstance(text, int):  # Convert numbers to strings
        return str(text)
    if not isinstance(text, str):
        return ""  # Handle NoneType or unexpected data types
    return ''.join(
        c if ord(c) < 128 else unicodedata.normalize('NFKD', c).encode('ascii', 'ignore').decode('ascii')
        for c in text
    )

def json_to_pdf(json_data, filename, title, include_answers=False):
    """ Convert JSON data to a structured PDF file with proper encoding. """
    try:
        print(f"✅ Generating PDF: {filename}")

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # ✅ Set Title
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, clean_text(title), ln=True, align='C')
        pdf.ln(10)

        # ✅ Validate JSON Structure
        if not isinstance(json_data, dict):
            print("❌ Error: Invalid JSON structure (Expected a dictionary)")
            return False

        # ✅ Extract Paper Metadata (Ensure conversion to string)
        paper_id = clean_text(json_data.get("paper_id", "N/A"))
        class_name = clean_text(json_data.get("class_name", "N/A"))
        subject = clean_text(json_data.get("subject", "N/A"))
        chapter = clean_text(json_data.get("chapter", "N/A"))
        topic = clean_text(json_data.get("topic", "N/A"))

        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 8, f"Paper ID: {paper_id}", ln=True)
        pdf.cell(200, 8, f"Class: {class_name}", ln=True)
        pdf.cell(200, 8, f"Subject: {subject}", ln=True)
        pdf.cell(200, 8, f"Chapter: {chapter}", ln=True)
        pdf.cell(200, 8, f"Topic: {topic}", ln=True)
        pdf.ln(10)

        # ✅ Section: Multiple Choice Questions (MCQs)
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(200, 8, "Multiple Choice Questions (Darken the circle around the second character including point):", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", size=12)
        mcqs = json_data.get("mcqs", [])
        if not isinstance(mcqs, list):
            print("⚠️ Warning: MCQs data is not a list, skipping...")
            mcqs = []
        for i, q in enumerate(mcqs, start=1):
            pdf.multi_cell(0, 8, clean_text(f"{i}. {q.get('question', '')}"))
            options = q.get("options", [])
            if isinstance(options, list):
                for j, option in enumerate(options):
                    pdf.multi_cell(0, 8, clean_text(f"    {chr(65 + j)}. {option}"))
            if include_answers:
                pdf.set_text_color(0, 128, 0)  # Green color for answer
                pdf.multi_cell(0, 8, clean_text(f"    ✅ Answer: {q.get('answer', '')}"))
                pdf.set_text_color(0, 0, 0)  # Reset text color
            pdf.ln(5)

        # ✅ Section: Fill in the Blanks
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(200, 8, "Fill in the Blanks (Write your answer at the end of each sentence after \"Ans:\"):", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", size=12)
        blanks = json_data.get("fill_in_the_blanks", [])
        if not isinstance(blanks, list):
            print("⚠️ Warning: Fill in the blanks data is not a list, skipping...")
            blanks = []
        for i, q in enumerate(blanks, start=1):
            pdf.multi_cell(0, 8, clean_text(f"{i}. {q.get('question', '')} Ans:"))
            if include_answers:
                pdf.set_text_color(0, 128, 0)
                pdf.multi_cell(0, 8, clean_text(f"    ✅ Answer: {q.get('answer', '')}"))
                pdf.set_text_color(0, 0, 0)
            pdf.ln(5)

        # ✅ Section: Short Answer Questions
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(200, 8, "Short Answer Questions (max 2-3 lines):", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", size=12)
        short_questions = json_data.get("short_questions", [])
        if not isinstance(short_questions, list):
            print("⚠️ Warning: Short answer questions data is not a list, skipping...")
            short_questions = []
        for i, q in enumerate(short_questions, start=1):
            pdf.multi_cell(0, 8, clean_text(f"{i}. {q.get('question', '')}"))
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 8, "Ans: ________________")  # Placeholder for the answer
            pdf.multi_cell(0, 8, "    ________________")  # Additional line if needed
            pdf.multi_cell(0, 8, "    ________________")  # Additional line if needed
            pdf.ln(5)

        # ✅ Save PDF
        pdf.output(filename, "F")
        print(f"✅ PDF Successfully Created: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error in json_to_pdf: {e}")
        return False

    
# ✅ API Endpoint: Download Questions as PDF (Without Answers)
@api_assessment_routes.route('/api/download_questions_pdf/<int:paper_id>', methods=['GET'])
def download_questions_pdf(paper_id):
    """ Download the questions JSON as a structured PDF file. """
    try:
        question_file = os.path.join(ANSWER_KEY_DIR, f"{paper_id}.json")
        if not os.path.exists(question_file):
            print("❌ Error: Question file not found")
            return jsonify({"error": "Question file not found"}), 404

        with open(question_file, "r", encoding="utf-8") as f:
            questions = json.load(f)

        pdf_filename = os.path.join(ANSWER_KEY_DIR, f"{paper_id}_questions.pdf")
        success = json_to_pdf(questions, pdf_filename, "Generated Question Paper", include_answers=False)

        if not success:
            print("❌ Error: PDF generation failed")
            return jsonify({"error": "Failed to generate PDF"}), 500

        return send_file(pdf_filename, as_attachment=True)

    except Exception as e:
        print(f"❌ Error downloading questions PDF: {e}")
        return jsonify({"error": "Failed to generate PDF"}), 500


@api_assessment_routes.route('/api/download_answers_pdf/<int:paper_id>', methods=['GET'])
def download_answers_pdf(paper_id):
    """ Download the answers JSON as a structured PDF file. """
    try:
        answer_file = os.path.join(ANSWER_KEY_DIR, f"{paper_id}_answers.json")
        if not os.path.exists(answer_file):
            print("❌ Error: Answer file not found")
            return jsonify({"error": "Answer file not found"}), 404

        with open(answer_file, "r", encoding="utf-8") as f:
            answers = json.load(f)

        pdf_filename = os.path.join(ANSWER_KEY_DIR, f"{paper_id}_answers.pdf")
        success = json_to_pdf(answers, pdf_filename, "Answer Key", include_answers=True)

        if not success:
            print("❌ Error: PDF generation failed")
            return jsonify({"error": "Failed to generate PDF"}), 500

        return send_file(pdf_filename, as_attachment=True)

    except Exception as e:
        print(f"❌ Error downloading answers PDF: {e}")
        return jsonify({"error": "Failed to generate PDF"}), 500
