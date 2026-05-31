from flask import Blueprint, request, jsonify, session
import openai
import re
import json
import os

# Initialize a Flask Blueprint
api_routes = Blueprint('api_routes', __name__)

# Load fine-tuned model training data (with NCERT Content)
FINE_TUNED_DATA_PATH = "fine_tuning_data.jsonl"
with open(FINE_TUNED_DATA_PATH, "r") as file:
    ncert_fine_tuned_data = [json.loads(line) for line in file]

# Initialize OpenAI client
def initialize_client():
    """
    Initialize the OpenAI client with the fine-tuned API key.
    """
    return openai.OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )

# Generate Summary with Two-Layer Fine-Tuned Model
def generate_summary_with_fine_tuned_model(class_name, subject, chapter, topic):
    """
    Bellow is just an example to imagine how code will work
    Generate a structured summary using a fine-tuned GPT model based on NCERT content 
    and additional user inputs.

    Parameters:
    - class_name (str): The class of the student (e.g., "Class 9").
    - subject (str): The subject (e.g., "Chemistry").
    - chapter (str): The chapter name (e.g., "Periodic Table").
    - topic (str): The specific topic of interest.

    Returns:
    - str: A structured, personalized summary.
    """
    client = initialize_client()

    try:
        fine_tuned_model = "gpt-4o-mini"

        # Retrieve relevant NCERT content for fine-tuning
        ncert_context = ""
        for entry in ncert_fine_tuned_data:
            if chapter.lower() in entry["messages"][1]["content"].lower():
                ncert_context = entry["messages"][1]["content"]
                break
        
        # User-specific context tuning
        prompt = f"""
        Generate a detailed yet easy-to-understand summary for the following details:
        - Class: {class_name}
        - Subject: {subject}
        - Chapter: {chapter}
        - Topic: {topic}
        
        Base your response on the following fine-tuned NCERT content:
        {ncert_context}
        
        The summary should:
        1. Be educational and structured.
        2. Use clear, simple language.
        3. Include key concepts and explanations.
        """

        # Generate summary using fine-tuned model
        response = client.chat.completions.create(
            model=fine_tuned_model,
            messages=[
                {"role": "system", "content": "You are an AI tutor specializing in NCERT syllabus."},
                {"role": "user", "content": prompt}
            ]
        )

        summary = response.choices[0].message.content.strip()
        return format_summary(summary)

    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        return "Failed to generate summary."

# Convert Markdown-style text to proper HTML formatting (to make sure generated output should be in good structure)
def format_summary(summary):
    formatted = []
    lines = summary.split("\n")
    in_list = False

    for line in lines:
        line = line.strip()

        # Convert bold text (**bold text** → <b>bold text</b>)
        line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)

        # Convert headings
        if line.startswith("#### "):
            formatted.append(f"<h4>{line[5:].strip()}</h4>")
        elif line.startswith("### "):
            formatted.append(f"<h3>{line[4:].strip()}</h3>")
        elif line.startswith("## "):
            formatted.append(f"<h2>{line[3:].strip()}</h2>")
        elif line.startswith("# "):
            formatted.append(f"<h1>{line[2:].strip()}</h1>")

        # Convert bullet points
        elif line.startswith("- "):
            if not in_list:
                formatted.append("<ul>")
                in_list = True
            formatted.append(f"<li>{line[2:].strip()}</li>")

        # Convert paragraphs
        elif line:
            formatted.append(f"<p>{line}</p>")

    if in_list:
        formatted.append("</ul>")

    return "".join(formatted)

# Chat with Bot (Fine-Tuned)
def chat_with_bot(query, chapter_context):
    """
    Chatbot function to generate concise, personalized responses (2-3 lines).
    """
    client = initialize_client()

    try:
        fine_tuned_model = "gpt-4o-mini"

        # First, generate detailed response
        response = client.chat.completions.create(
            model=fine_tuned_model,
            max_tokens=300,
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are an AI tutor specializing in {chapter_context}. "
                        "Explain concepts clearly using NCERT knowledge."
                    )
                },
                {"role": "user", "content": query}
            ]
        )

        full_response = response.choices[0].message.content.strip()

        # Summarize the response in 2-3 sentences
        summary_prompt = f"""
        Summarize the following explanation in 2-3 lines while keeping key details:
        "{full_response}"
        
        Ensure:
        1. It remains clear and concise.
        2. Key points are preserved.
        3. Easy language is used for better understanding.
        """

        summary_response = client.chat.completions.create(
            model=fine_tuned_model,
            max_tokens=100,
            temperature=0.5,
            messages=[
                {"role": "system", "content": "You are a summarization assistant."},
                {"role": "user", "content": summary_prompt}
            ]
        )

        return summary_response.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ Error in chatbot interaction: {e}")
        return "Sorry, I couldn't generate a response. Please try again later."

# API Route for Summarization
@api_routes.route('/api/summarize', methods=['POST'])
def summarize():
    """
    API endpoint for generating a summary.
    """
    try:
        data = request.json
        class_name = data.get('class_name', '').strip()
        subject = data.get('subject', '').strip()
        chapter = data.get('chapter', '').strip()
        topic = data.get('topic', '').strip()

        if not class_name or not subject or not chapter or not topic:
            return jsonify({'error': 'All fields are required.'}), 400

        session.update({"class_name": class_name, "subject": subject, "chapter": chapter, "topic": topic})

        summary = generate_summary_with_fine_tuned_model(class_name, subject, chapter, topic)
        return jsonify({'summary': summary}) if summary != "Failed to generate summary." else jsonify({'error': summary}), 500

    except Exception as e:
        print(f"❌ Error in summarize endpoint: {e}")
        return jsonify({'error': 'An error occurred. Please try again later.'}), 500

# API Route for Chatbot
@api_routes.route('/api/chatbot', methods=['POST'])
def chatbot():
    """
    API endpoint to handle chatbot queries.
    """
    try:
        data = request.json
        query = data.get('query', '').strip()
        chapter_context = data.get('chapter_context', '').strip()

        if not query or not chapter_context:
            return jsonify({'error': 'Query and chapter context are required.'}), 400

        response = chat_with_bot(query, chapter_context)
        return jsonify({'response': response})

    except Exception as e:
        print(f"❌ Error in chatbot endpoint: {e}")
        return jsonify({'error': 'An error occurred. Please try again later.'}), 500
