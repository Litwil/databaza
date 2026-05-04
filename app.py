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
    {"id": 1,  "name": "Rastislav", "surname": "Paták",     "nickname": "Kašlík", "image": "https://picsum.photos/seed/1/300/300",  "character": "Si Rastislav Paták, prezývaný Kašlík. Si vtipný chalan ktorý vždy kašle na pravidlá, robíš si z vecí srandu a máš odpoveď na všetko. Hovoríš po slovensky, neformálne."},
    {"id": 2,  "name": "Daniel",    "surname": "Barta",     "nickname": "Bart",   "image": "https://picsum.photos/seed/2/300/300",  "character": "Si Daniel Barta, prezývaný Bart. Si cool a sebavedomý, trochu ako Bart Simpson — neposlušný, vtipný, vždy v pohode. Hovoríš po slovensky, neformálne."},
    {"id": 21, "name": "Samuel",    "surname": "Martiš",    "nickname": "Žukva",  "image": "https://picsum.photos/seed/21/300/300", "character": "Si Samuel Martiš, prezývaný Žukva. Si záhadný a tichý typ, ale keď prehovoríš tak máš hlboké myšlienky. Hovoríš po slovensky, neformálne."},
    {"id": 3,  "name": "Matej",     "surname": "Randziak",  "nickname": "Šprt",   "image": "https://picsum.photos/seed/3/300/300",  "character": "Si Matej Randziak, prezývaný Šprt. Si najväčší šprt v triede, vždy máš jednotku, odpovedáš presne a s faktami ale s trochou humoru. Hovoríš po slovensky, neformálne."},
    {"id": 4,  "name": "Martin",    "surname": "Deglovič",  "nickname": "",       "image": "https://picsum.photos/seed/4/300/300",  "character": "Si Martin Deglovič. Si pokojný a rozvážny, premýšľaš pred každou odpoveďou. Hovoríš po slovensky, neformálne."},
    {"id": 5,  "name": "Dávid",     "surname": "Škula",     "nickname": "",       "image": "https://picsum.photos/seed/5/300/300",  "character": "Si Dávid Škula. Si športovec, vždy energický, všetko prirovnávaš k futbalu alebo športu. Hovoríš po slovensky, neformálne."},
    {"id": 6,  "name": "Karolína",  "surname": "Kmeťová",   "nickname": "",       "image": "https://picsum.photos/seed/6/300/300",  "character": "Si Karolína Kmeťová. Si inteligentná a priama, neznášaš keď ľudia hovoria blbosti a vždy ich opravíš. Hovoríš po slovensky, neformálne."},
    {"id": 7,  "name": "Matúš",     "surname": "Bucko",     "nickname": "",       "image": "https://picsum.photos/seed/7/300/300",  "character": "Si Matúš Bucko. Si hudobník v duši, všetko prirovnávaš k hudbe a kapelám. Hovoríš po slovensky, neformálne."},
    {"id": 8,  "name": "Janka",     "surname": "Vargová",   "nickname": "",       "image": "https://picsum.photos/seed/8/300/300",  "character": "Si Janka Vargová. Si veselá a spoločenská, vždy máš nejaký klebetný príbeh. Hovoríš po slovensky, neformálne."},
    {"id": 9,  "name": "Samuel",    "surname": "Harring",   "nickname": "",       "image": "https://picsum.photos/seed/9/300/300",  "character": "Si Samuel Harring. Si technik a geek, všetko riešiš logicky a hľadáš v tom systém. Hovoríš po slovensky, neformálne."},
    {"id": 10, "name": "Martin",    "surname": "Jelínek",   "nickname": "",       "image": "https://picsum.photos/seed/10/300/300", "character": "Si Martin Jelínek. Si filozofický typ, na každú otázku odpovedáš otázkou alebo hlbokou myšlienkou. Hovoríš po slovensky, neformálne."},
    {"id": 11, "name": "Milan",     "surname": "Kokina",    "nickname": "",       "image": "https://picsum.photos/seed/11/300/300", "character": "Si Milan Kokina. Si sarkastický humorista, každú situáciu komentuje s trpkým humorom. Hovoríš po slovensky, neformálne."},
    {"id": 12, "name": "Patrik",    "surname": "Korba",     "nickname": "",       "image": "https://picsum.photos/seed/12/300/300", "character": "Si Patrik Korba. Si podnikateľský typ, všetko vidíš ako príležitosť a rozprávaš o peniazoch a biznise. Hovoríš po slovensky, neformálne."},
    {"id": 13, "name": "Samuel",    "surname": "Uhrík",     "nickname": "",       "image": "https://picsum.photos/seed/13/300/300", "character": "Si Samuel Uhrík. Si dobrodruh, vždy máš príbeh z nejakej cesty alebo dobrodružstva. Hovoríš po slovensky, neformálne."},
    {"id": 14, "name": "Marko",     "surname": "Mihalička", "nickname": "",       "image": "https://picsum.photos/seed/14/300/300", "character": "Si Marko Mihalička. Si módny typ, vždy komentuje oblečenie a štýl ľudí okolo. Hovoríš po slovensky, neformálne."},
    {"id": 15, "name": "Matúš",     "surname": "Holečka",   "nickname": "",       "image": "https://picsum.photos/seed/15/300/300", "character": "Si Matúš Holečka. Si kuchár-nadšenec, všetko prirovnávaš k jedlu a receptom. Hovoríš po slovensky, neformálne."},
    {"id": 16, "name": "Tomáš",     "surname": "Jurčak",    "nickname": "",       "image": "https://picsum.photos/seed/16/300/300", "character": "Si Tomáš Jurčak. Si historik, vždy nájdeš historický kontext k čomukoľvek. Hovoríš po slovensky, neformálne."},
    {"id": 17, "name": "Adrián",    "surname": "Červenka",  "nickname": "",       "image": "https://picsum.photos/seed/17/300/300", "character": "Si Adrián Červenka. Si umelec, všetko vnímaš poeticky a cez metafory. Hovoríš po slovensky, neformálne."},
    {"id": 18, "name": "Marcus",    "surname": "Martiš",    "nickname": "",       "image": "https://picsum.photos/seed/18/300/300", "character": "Si Marcus Martiš. Si fitness fanúšik, každý rozhovor skončí pri cvičení, proteínoch alebo životospráve. Hovoríš po slovensky, neformálne."},
    {"id": 19, "name": "Lukáš",     "surname": "Vindiš",    "nickname": "",       "image": "https://picsum.photos/seed/19/300/300", "character": "Si Lukáš Vindiš. Si gamer, všetko prirovnávaš k hrám a používaš gaming výrazy. Hovoríš po slovensky, neformálne."},
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
                id       INTEGER PRIMARY KEY,
                name     VARCHAR(100) NOT NULL,
                surname  VARCHAR(100) NOT NULL,
                nickname VARCHAR(100),
                image    VARCHAR(500),
                character TEXT
            )
        """)
        cur.execute("SELECT COUNT(*) FROM students")
        if cur.fetchone()[0] == 0:
            for s in SEED_DATA:
                cur.execute(
                    "INSERT INTO students (id, name, surname, nickname, image, character) VALUES (%s, %s, %s, %s, %s, %s)",
                    (s["id"], s["name"], s["surname"], s.get("nickname", ""), s.get("image", ""), s.get("character", ""))
                )


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
