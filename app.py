from flask import Flask, render_template, session
from datetime import datetime
import os

# Import Blueprints
from api_routes import api_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Necessary if using sessions

# Static Data for Topics
topics = [
    {'id': 1, 'title': 'Physics', 'summary': 'Learn about the fundamental principles of physics.'},
    {'id': 2, 'title': 'Chemistry', 'summary': 'Explore the reactions that shape our world.'},
    {'id': 3, 'title': 'Biology', 'summary': 'Discover the building blocks of life.'}
]

# ================== Blueprint Registration ================== #
try:
    # Regular API Routes
    from api_routes import api_routes
    app.register_blueprint(api_routes)
    
    # Assessment Routes
    from api_assessment_routes import api_assessment_routes
    app.register_blueprint(api_assessment_routes)
    print("✅ API Assessment Routes Registered Successfully")
    
    # Evaluation Routes
    from api_evaluation_routes import api_evaluation_routes  
    app.register_blueprint(api_evaluation_routes)
    print("✅ API Evaluation Routes Registered Successfully")

except ImportError as e:
    print(f"⚠️ Warning: Could not import routes - {e}")
    if 'api_assessment_routes' in str(e):
        print("⚠️ Assessment features disabled")
    if 'api_evaluation_routes' in str(e):
        print("⚠️ Evaluation features disabled")

# ================== Core Routes ================== #
@app.route('/')
def index():
    return render_template('index.html', topics=topics, time=datetime.now())

@app.route('/summary/<int:topic_id>')
def summary(topic_id):
    topic = next((t for t in topics if t['id'] == topic_id), None)
    return render_template('summary.html', topic=topic, time=datetime.now()) if topic else ("Topic not found", 404)

@app.route('/assessments/<int:topic_id>')
def assessments(topic_id):
    return render_template('assessments.html', topic_id=topic_id, time=datetime.now())

@app.route('/evaluate/<int:assessment_id>', methods=['GET', 'POST'])
def submit(assessment_id):
    return render_template('evaluate.html', assessment_id=assessment_id, time=datetime.now())

@app.route('/about/<int:submission_id>')
def evaluate(submission_id):
    return render_template('about.html', submission_id=submission_id, time=datetime.now())

if __name__ == "__main__":
    app.run(debug=True)