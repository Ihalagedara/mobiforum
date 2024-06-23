from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)
DATABASE = 'questions.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT id, title, content FROM questions ORDER BY id DESC')
    questions = cur.fetchall()
    return render_template('index.html', questions=questions)

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db = get_db()
        db.execute('INSERT INTO questions (title, content) VALUES (?, ?)', (title, content))
        db.commit()
        return redirect(url_for('index'))
    return render_template('ask.html')

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question(question_id):
    db = get_db()
    if request.method == 'POST':
        answer = request.form['answer']
        db.execute('INSERT INTO answers (question_id, content) VALUES (?, ?)', (question_id, answer))
        db.commit()
    question = db.execute('SELECT id, title, content FROM questions WHERE id = ?', (question_id,)).fetchone()
    answers = db.execute('SELECT content FROM answers WHERE question_id = ?', (question_id,)).fetchall()
    return render_template('question.html', question=question, answers=answers)

@app.route('/delete/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    db = get_db()
    db.execute('DELETE FROM questions WHERE id = ?', (question_id,))
    db.execute('DELETE FROM answers WHERE question_id = ?', (question_id,))
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000,debug=True)
