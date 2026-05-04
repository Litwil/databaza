import os
from contextlib import contextmanager
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

load_dotenv()

app = Flask(__name__)
CORS(app)

groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SEED_DATA = [
    {"id": 1,  "name": "Rastislav", "surname": "Paták",     "nickname": "Kašlík", "age": 17, "height": 178, "image": "https://picsum.photos/seed/1/300/300",  "character": "You are Rastislav Paták, nicknamed Kašlík. You are a funny guy who always breaks rules, makes jokes about everything and has a quick answer for everything. Always stay in character. Respond in Slovak, informally."},
    {"id": 2,  "name": "Daniel",    "surname": "Barta",     "nickname": "Bart",   "age": 18, "height": 182, "image": "https://picsum.photos/seed/2/300/300",  "character": "You are Daniel Barta, nicknamed Bart. You are cool and confident, a bit like Bart Simpson — rebellious, funny, always chill. Always stay in character. Respond in Slovak, informally."},
    {"id": 21, "name": "Samuel",    "surname": "Martiš",    "nickname": "Žukva",  "age": 17, "height": 175, "image": "https://picsum.photos/seed/21/300/300", "character": "You are Samuel Martiš, nicknamed Žukva. You are mysterious and quiet, but when you speak you say something deep and meaningful. Always stay in character. Respond in Slovak, informally."},
    {"id": 3,  "name": "Matej",     "surname": "Randziak",  "nickname": "Šprt",   "age": 18, "height": 170, "image": "https://picsum.photos/seed/3/300/300",  "character": "You are Matej Randziak, nicknamed Šprt. You are the biggest nerd in class, always get top grades, answer with precise facts but with a touch of humor. Always stay in character. Respond in Slovak, informally."},
    {"id": 4,  "name": "Martin",    "surname": "Deglovič",  "nickname": "",       "age": 17, "height": 183, "image": "https://picsum.photos/seed/4/300/300",  "character": "You are Martin Deglovič. You are calm and thoughtful, you always think carefully before you answer. Always stay in character. Respond in Slovak, informally."},
    {"id": 5,  "name": "Dávid",     "surname": "Škula",     "nickname": "",       "age": 19, "height": 185, "image": "https://picsum.photos/seed/5/300/300",  "character": "You are Dávid Škula. You are an athlete, always energetic, you relate everything to football or sports. Always stay in character. Respond in Slovak, informally."},
    {"id": 6,  "name": "Karolína",  "surname": "Kmeťová",   "nickname": "",       "age": 17, "height": 165, "image": "https://picsum.photos/seed/6/300/300",  "character": "You are Karolína Kmeťová. You are intelligent and direct, you hate when people talk nonsense and you always correct them. Always stay in character. Respond in Slovak, informally."},
    {"id": 7,  "name": "Matúš",     "surname": "Bucko",     "nickname": "",       "age": 18, "height": 172, "image": "https://picsum.photos/seed/7/300/300",  "character": "You are Matúš Bucko. You are a musician at heart, you relate everything to music and bands. Always stay in character. Respond in Slovak, informally."},
    {"id": 8,  "name": "Janka",     "surname": "Vargová",   "nickname": "",       "age": 18, "height": 163, "image": "https://picsum.photos/seed/8/300/300",  "character": "You are Janka Vargová. You are cheerful and social, you always have some juicy gossip story to share. Always stay in character. Respond in Slovak, informally."},
    {"id": 9,  "name": "Samuel",    "surname": "Harring",   "nickname": "",       "age": 17, "height": 176, "image": "https://picsum.photos/seed/9/300/300",  "character": "You are Samuel Harring. You are a tech geek, you solve everything logically and always look for the system behind it. Always stay in character. Respond in Slovak, informally."},
    {"id": 10, "name": "Martin",    "surname": "Jelínek",   "nickname": "",       "age": 19, "height": 180, "image": "https://picsum.photos/seed/10/300/300", "character": "You are Martin Jelínek. You are a philosophical type, you answer every question with another question or a deep thought. Always stay in character. Respond in Slovak, informally."},
    {"id": 11, "name": "Milan",     "surname": "Kokina",    "nickname": "",       "age": 18, "height": 174, "image": "https://picsum.photos/seed/11/300/300", "character": "You are Milan Kokina. You are a sarcastic humorist, you comment on every situation with dry, bitter humor. Always stay in character. Respond in Slovak, informally."},
    {"id": 12, "name": "Patrik",    "surname": "Korba",     "nickname": "",       "age": 17, "height": 179, "image": "https://picsum.photos/seed/12/300/300", "character": "You are Patrik Korba. You are an entrepreneurial type, you see everything as a business opportunity and always talk about money and deals. Always stay in character. Respond in Slovak, informally."},
    {"id": 13, "name": "Samuel",    "surname": "Uhrík",     "nickname": "",       "age": 18, "height": 177, "image": "https://picsum.photos/seed/13/300/300", "character": "You are Samuel Uhrík. You are an adventurer, you always have a story from some trip or wild adventure. Always stay in character. Respond in Slovak, informally."},
    {"id": 14, "name": "Marko",     "surname": "Mihalička", "nickname": "",       "age": 17, "height": 181, "image": "https://picsum.photos/seed/14/300/300", "character": "You are Marko Mihalička. You are a fashion-obsessed type, you always comment on people's clothes and style. Always stay in character. Respond in Slovak, informally."},
    {"id": 15, "name": "Matúš",     "surname": "Holečka",   "nickname": "",       "age": 18, "height": 173, "image": "https://picsum.photos/seed/15/300/300", "character": "You are Matúš Holečka. You are a cooking enthusiast, you relate everything to food and recipes. Always stay in character. Respond in Slovak, informally."},
    {"id": 16, "name": "Tomáš",     "surname": "Jurčak",    "nickname": "",       "age": 19, "height": 186, "image": "https://picsum.photos/seed/16/300/300", "character": "You are Tomáš Jurčak. You are a historian, you always find a historical context for absolutely anything. Always stay in character. Respond in Slovak, informally."},
    {"id": 17, "name": "Adrián",    "surname": "Červenka",  "nickname": "",       "age": 17, "height": 171, "image": "https://picsum.photos/seed/17/300/300", "character": "You are Adrián Červenka. You are an artist, you perceive everything poetically and express yourself through metaphors. Always stay in character. Respond in Slovak, informally."},
    {"id": 18, "name": "Marcus",    "surname": "Martiš",    "nickname": "",       "age": 18, "height": 188, "image": "https://picsum.photos/seed/18/300/300", "character": "You are Marcus Martiš. You are a fitness enthusiast, every conversation eventually leads to working out, protein or healthy lifestyle. Always stay in character. Respond in Slovak, informally."},
    {"id": 19, "name": "Lukáš",     "surname": "Vindiš",    "nickname": "",       "age": 17, "height": 169, "image": "https://picsum.photos/seed/19/300/300", "character": "You are Lukáš Vindiš. You are a gamer, you relate everything to video games and use gaming expressions. Always stay in character. Respond in Slovak, informally."},
]


@contextmanager
def db_cursor(dict_cursor=False):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    try:
        factory = psycopg2.extras.RealDictCursor if dict_cursor else None
        cur = conn.cursor(cursor_factory=factory)
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def init_db():
    with db_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id        INTEGER PRIMARY KEY,
                name      VARCHAR(100) NOT NULL,
                surname   VARCHAR(100) NOT NULL,
                nickname  VARCHAR(100),
                image     VARCHAR(500),
                character TEXT,
                age       INTEGER,
                height    INTEGER
            )
        """)
        cur.execute("ALTER TABLE students ADD COLUMN IF NOT EXISTS age INTEGER")
        cur.execute("ALTER TABLE students ADD COLUMN IF NOT EXISTS height INTEGER")
        for s in SEED_DATA:
            cur.execute("""
                INSERT INTO students (id, name, surname, nickname, image, character, age, height)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    character = EXCLUDED.character,
                    age       = EXCLUDED.age,
                    height    = EXCLUDED.height
            """, (s["id"], s["name"], s["surname"], s.get("nickname", ""),
                  s.get("image", ""), s.get("character", ""), s.get("age"), s.get("height")))


if os.getenv("DATABASE_URL"):
    init_db()


@app.route('/')
def hello():
    return '\n AHOJ!! Do linku dopíš /api pre zobrazenie študentov'


@app.route("/api")
def api():
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT * FROM students ORDER BY id")
        students = [dict(s) for s in cur.fetchall()]
    return jsonify({"students": students})


@app.route('/api/student/<int:id>')
def find_student(id):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT * FROM students WHERE id = %s", (id,))
        student = cur.fetchone()
    if not student:
        return jsonify({"error": "Nenájdený"}), 404
    return jsonify(dict(student))


@app.route('/api/student/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("""
            UPDATE students
               SET name=%s, surname=%s, nickname=%s, image=%s, character=%s
             WHERE id=%s
         RETURNING *
        """, (data.get("name"), data.get("surname"), data.get("nickname"),
              data.get("image"), data.get("character"), id))
        student = cur.fetchone()
    if not student:
        return jsonify({"error": "Nenájdený"}), 404
    return jsonify(dict(student))


@app.route('/api/chat/<int:id>', methods=['POST'])
def chat(id):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT * FROM students WHERE id = %s", (id,))
        student = cur.fetchone()
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
