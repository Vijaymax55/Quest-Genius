import os
import json
import pdfplumber  # Use pdfplumber instead of PyPDF2 for better pdf documentation related operations 

# Define the folder path for the NCERT Content few chapters were missing 
learning_materials_path = "learning_materials"

# Structure for storing training data
training_data = []

# Loop through the classes and subjects
for class_folder in os.listdir(learning_materials_path):
    class_path = os.path.join(learning_materials_path, class_folder)
    if os.path.isdir(class_path):
        for pdf_file in os.listdir(class_path):
            if pdf_file.endswith(".pdf"):
                pdf_path = os.path.join(class_path, pdf_file)

                try:
                    # Read PDF content using pdfplumber
                    with pdfplumber.open(pdf_path) as pdf:
                        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

                    # Handle cases where the PDF contains images instead of text
                    if not text.strip():
                        text = "No readable text found. This might be a scanned document."

                    # Create structured JSONL format
                    training_data.append({
                        "messages": [
                            {"role": "system", "content": f"You are an AI tutor for {class_folder}."},
                            {"role": "user", "content": f"Summarize this content: {text[:2000]}"},
                            {"role": "assistant", "content": f"{text[:500]}... (Summary continues)"},
                        ]
                    })
                
                except Exception as e:
                    print(f"Error processing {pdf_file}: {e}")

# Save data for fine-tuning
with open("fine_tuning_data.jsonl", "w") as f:
    for entry in training_data:
        f.write(json.dumps(entry) + "\n")

print("Training data prepared!")
