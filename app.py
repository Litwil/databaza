import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
from db import get_all_students, get_student_by_id

load_dotenv()

app = Flask(__name__)
CORS(app)

groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

@app.route('/')
def hello():
    return '\n AHOJ!! Do linku dopíš /api pre zobrazenie študentov'


@app.route("/api")
def api():
    students = get_all_students()
    return jsonify({"students": students})


@app.route('/api/student/<int:id>')
def find_student(id):
    student = get_student_by_id(id)
    if not student:
        return jsonify({"error": "Nenájdený"}), 404
    return jsonify(student)


@app.route('/api/chat/<int:id>', methods=['POST'])
def chat(id):
    student = get_student_by_id(id)
    if not student:
        return jsonify({"error": "Nenájdený"}), 404

    body = request.get_json()
    messages = body.get("messages", [])

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": student["character"]},
            *messages
        ]
    )

    return jsonify({"reply": response.choices[0].message.content})


if __name__ == "__main__":
    app.run(debug=True)
