from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure random key

# Home page with links to study sections and quiz
@app.route('/')
def index():
    return render_template('index.html')

# Study page for a specific section (lymphatic, respiratory, digestive)
@app.route('/study/<section>')
def study(section):
    valid_sections = ['lymphatic', 'respiratory', 'digestive']
    if section not in valid_sections:
        return "Section not found", 404
    # Load the corresponding HTML content from the knowledge base folder
    with open(os.path.join('data', 'knowledge', f'{section}.html'), 'r', encoding='utf-8') as file:
        content = file.read()
    return render_template('study.html', section=section.capitalize(), content=content)

# Quiz page: display questions and process responses
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    with open(os.path.join('data', 'quizzes.json'), 'r', encoding='utf-8') as f:
        quiz_data = json.load(f)
    
    results = None
    if request.method == 'POST':
        user_answers = request.form.to_dict()
        results = {}
        for q in quiz_data['questions']:
            qid = q['id']
            expected = q['answer'].strip().lower()
            user_response = user_answers.get(qid, "").strip().lower()
            results[qid] = (user_response == expected)
    
    return render_template('quiz.html', quiz=quiz_data, results=results)

if __name__ == '__main__':
    app.run(debug=True)
