from flask import Blueprint, request, jsonify
from PIL import Image
import pytesseract
import re
import json
from fuzzywuzzy import fuzz
import os
import openai

# Define Blueprint for Evaluation Routes
api_evaluation_routes = Blueprint("api_evaluation_routes", __name__)

# ✅ Ensure Answer Key Directory Exists
ANSWER_KEY_DIR = "answerkey"
os.makedirs(ANSWER_KEY_DIR, exist_ok=True)

# Initialize the OpenAI client
def initialize_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is missing. Please set it in the code or as an environment variable.")
    client = openai.OpenAI(api_key=api_key)
    return client

client = initialize_client()

# ✅ Evaluation Route: Evaluate Uploaded Images
@api_evaluation_routes.route('/api/evaluate_assessment', methods=['POST'])
def evaluate_assessment():
    """Evaluate uploaded images and return evaluation results."""
    try:
        # Get the paper ID
        paper_id = request.form.get('paper_id')
        if not paper_id:
            return jsonify({"error": "Paper ID is required"}), 400

        # Load the answer key
        answer_key_path = os.path.join(ANSWER_KEY_DIR, f"{paper_id}_answers.json")
        if not os.path.exists(answer_key_path):
            return jsonify({"error": "Answer key not found"}), 404

        with open(answer_key_path, 'r') as file:
            answer_key = json.load(file)

        # Get uploaded files
        uploaded_files = request.files.getlist('images')
        if len(uploaded_files) != 3:
            return jsonify({"error": "Exactly 3 images are required"}), 400

        # Save uploaded files
        image_paths = []
        for file in uploaded_files:
            if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filename = os.path.join(ANSWER_KEY_DIR, file.filename)
                file.save(filename)
                image_paths.append(filename)

        # Extract text from images
        combined_text = extract_text_from_images(image_paths)

        # Parse questions
        mcqs, fills, shorts = parse_questions(combined_text)

        # Evaluate MCQs
        mcq_results = evaluate_mcqs(combined_text, len(answer_key["mcqs"]), answer_key)

        # Evaluate Fill-in-the-blanks
        fill_score, fill_results = evaluate_fills_and_shorts(fills, answer_key, "fill_in_the_blanks")

        # Evaluate Short Answer Questions
        short_score, short_results = evaluate_fills_and_shorts(shorts, answer_key, "short_questions")

        # Generate feedback for fill-in-the-blanks and short answers using GPT
        for result in fill_results:
            result["feedback"] = get_feedback(client, result["question"], result["student_answer"], result["correct_answer"])
        for result in short_results:
            result["feedback"] = get_feedback(client, result["question"], result["student_answer"], result["correct_answer"])

        # Combine all results
        evaluation_results = mcq_results + fill_results + short_results

        # Calculate total score
        total_score = sum(result["score"] for result in evaluation_results)

        # Return evaluation results
        return jsonify({
            "evaluation_results": evaluation_results,
            "total_score": total_score
        })

    except Exception as e:
        print(f"❌ Error in evaluate_assessment: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

# ✅ Helper Function: Extract Text from Images
def extract_text_from_images(image_paths):
    """Extract text from multiple images using OCR and combine it."""
    full_text = ""
    for path in image_paths:
        try:
            img = Image.open(path)
            text = pytesseract.image_to_string(img)
            full_text += text + "\n"
        except Exception as e:
            print(f"❌ Error processing {path}: {e}")
    return full_text



# ✅ Helper Function: Parse Questions from OCR Text
def parse_questions(text):
    """
    Parse the questions and answers from the OCR text.
    The text is first split into sections based on unique headers:
        - Multiple Choice Questions:
        - Fill in the Blanks:
        - Short Answer Questions:
    """
    # Initialize sections
    mcq_section = ""
    fill_section = ""
    short_section = ""

    # Split text into sections using known markers
    if "Multiple Choice Questions:" in text:
        # Everything after this marker is considered MCQs and subsequent sections.
        _, rest = text.split("Multiple Choice Questions:", 1)

        # Look for the Fill in the Blanks section marker
        if "Fill in the Blanks:" in rest:
            mcq_section, remainder = rest.split("Fill in the Blanks:", 1)
            # Look for the Short Answer Questions marker in the remainder
            if "Short Answer Questions:" in remainder:
                fill_section, short_section = remainder.split("Short Answer Questions:", 1)
            else:
                fill_section = remainder
        elif "Short Answer Questions:" in rest:
            mcq_section, short_section = rest.split("Short Answer Questions:", 1)
        else:
            mcq_section = rest
    else:
        # Fallback: if no marker is found, consider all text as one section.
        mcq_section = text

    # ----- Extract MCQs -----
    mcqs = {}
    # This regex is designed to capture MCQs with a number, question text, option labels, etc.
    mcq_pattern = re.compile(r'(\d+)\.\s(.*?)([A-D]\.)(.*?)(?=\n\d|\Z)', re.DOTALL)
    for match in mcq_pattern.finditer(mcq_section):
        mcqs[match.group(1)] = {
            'marked_answer': match.group(4).strip()
        }

    # ----- Extract Fill in the Blanks -----
    fills = {}
    # Updated regex: accepts a period or comma after the number and captures multiline answers
    fill_pattern = re.compile(
        r'\b(\d+)[\.,]\s.*?Ans:\s*(.*?)(?=\n\s*\d+[\.,]\s|$)',
        re.DOTALL | re.IGNORECASE
    )
    for match in fill_pattern.finditer(fill_section):
        fills[match.group(1)] = {
            'marked_answer': match.group(2).strip()
        }

    # ----- Extract Short Answer Questions -----
    shorts = {}
    # Updated regex for short answers
    short_pattern = re.compile(
        r'\b(\d+)[\.,]\s.*?Ans:\s*(.*?)(?=\n\s*\d+[\.,]\s|$)',
        re.DOTALL | re.IGNORECASE
    )
    for match in short_pattern.finditer(short_section):
        shorts[match.group(1)] = {
            'marked_answer': match.group(2).strip()
        }

    return mcqs, fills, shorts



# ✅ Helper Function: Evaluate MCQs
def evaluate_mcqs(extracted_text, num_questions, answer_key):
    """Evaluate Multiple Choice Questions and provide feedback."""
    results = []
    questions = re.split(r'\n\d+\.\s', extracted_text)  # Split by question numbers
    for idx, q in enumerate(questions[1:], start=1):  # Skip first empty split
        if idx > num_questions:
            break
        options = re.findall(r'([A-D])\.\s*([^\n]*)', q, flags=re.IGNORECASE)
        marked_option = None
        feedback = "No option selected."
        for opt_letter, text in options:
            if re.search(r'[@●*✓®]', text):
                marked_option = f"{opt_letter.upper()}."

        correct_answer = answer_key["mcqs"][idx-1]["answer"]
        is_correct = marked_option == correct_answer.split()[0] if marked_option else False
        feedback = "Correct" if is_correct else "Incorrect"
        results.append({
            "serial_number": idx,  # Add serial number
            "question": answer_key["mcqs"][idx-1]["question"],
            "student_answer": marked_option or "No answer marked",
            "correct_answer": correct_answer,
            "feedback": feedback,
            "is_correct": is_correct,
            "score": 1 if is_correct else 0
        })
    return results

# ✅ Helper Function: Evaluate Fill-in-the-blanks and Short Answers
def evaluate_fills_and_shorts(questions, answer_key, question_type):
    """Evaluate fill-in-the-blanks and short answer questions."""
    total_score = 0
    results = []
    for q_num, info in questions.items():
        if int(q_num) - 1 >= len(answer_key[question_type]):
            continue  # Skip if there are more questions than answer_key entries
        correct_answer = answer_key[question_type][int(q_num) - 1]["answer"]
        student_answer = info["marked_answer"]
        is_correct = fuzz.ratio(student_answer.lower(), correct_answer.lower()) >= 40
        score = 1 if question_type == "fill_in_the_blanks" else 2
        if is_correct:
            total_score += score
        results.append({
            "serial_number": int(q_num),  # Add serial number
            "question": answer_key[question_type][int(q_num) - 1]["question"],
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "score": score if is_correct else 0
        })
    return total_score, results

# ✅ Helper Function: Generate Feedback using GPT
def get_feedback(client, question, student_answer, correct_answer):
    """Generate feedback using GPT."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI trained to provide educational feedback. Evaluate the student's answer for correctness and clarity."},
                {"role": "user", "content": f"Question: {question}\nStudent Answer: {student_answer}\nCorrect Answer: {correct_answer}"}
            ]
        )
        feedback = response.choices[0].message.content
    except Exception as e:
        feedback = f"Error in generating feedback: {e}"
    return feedback