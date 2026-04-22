from flask import Flask, render_template, request, redirect, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "secret123"

# DB
def get_db():
    conn = sqlite3.connect("song.db")
    conn.row_factory = sqlite3.Row
    return conn

# HASH
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# INIT DB
def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        file TEXT,
        image TEXT,
        plays INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        song_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= HOME =================
@app.route('/')
def home():
    conn = get_db()
    songs = conn.execute("SELECT * FROM songs").fetchall()
    conn.close()
    return render_template("index.html", songs=songs, liked_ids=[])

# ================= PLAY =================
@app.route('/play/<int:id>')
def play(id):
    conn = get_db()
    conn.execute("UPDATE songs SET plays = plays + 1 WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return ""

# ================= LIKE (SAFE TOGGLE) =================
@app.route('/like/<int:id>')
def like(id):
    user = session.get("user", "guest")

    conn = get_db()
    c = conn.cursor()

    existing = c.execute(
        "SELECT * FROM likes WHERE username=? AND song_id=?",
        (user, id)
    ).fetchone()

    if existing:
        c.execute("DELETE FROM likes WHERE username=? AND song_id=?", (user, id))
    else:
        c.execute("INSERT INTO likes(username, song_id) VALUES (?,?)", (user, id))

    conn.commit()
    conn.close()

    return redirect('/')

# ================= TRENDING =================
@app.route('/trending')
def trending():
    conn = get_db()
    songs = conn.execute(
        "SELECT * FROM songs ORDER BY plays DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return render_template("index.html", songs=songs, liked_ids=[])

# ================= AI RECOMMEND =================
@app.route('/recommend')
def recommend():
    user = session.get("user", "guest")
    conn = get_db()

    # liked songs
    liked = conn.execute(
        "SELECT song_id FROM likes WHERE username=?",
        (user,)
    ).fetchall()

    liked_ids = [str(i["song_id"]) for i in liked]

    if liked_ids:
        query = f"""
        SELECT * FROM songs
        WHERE id NOT IN ({','.join(liked_ids)})
        ORDER BY plays DESC LIMIT 5
        """
    else:
        query = "SELECT * FROM songs ORDER BY RANDOM() LIMIT 5"

    songs = conn.execute(query).fetchall()
    conn.close()

    return render_template("index.html", songs=songs, liked_ids=[])

# ================= SEARCH =================
@app.route('/search')
def search():
    q = request.args.get("q")

    conn = get_db()
    songs = conn.execute(
        "SELECT * FROM songs WHERE name LIKE ?",
        ('%'+q+'%',)
    ).fetchall()
    conn.close()

    return render_template("index.html", songs=songs, liked_ids=[])

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)