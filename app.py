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

# ================= TRENDING =================
@app.route('/trending')
def trending():
    conn = get_db()
    songs = conn.execute("SELECT * FROM songs ORDER BY plays DESC LIMIT 10").fetchall()
    conn.close()
    return render_template("index.html", songs=songs, liked_ids=[])

# ================= RECOMMEND =================
@app.route('/recommend')
def recommend():
    conn = get_db()

    # SAFE QUERY (no crash)
    songs = conn.execute("SELECT * FROM songs ORDER BY RANDOM() LIMIT 5").fetchall()

    conn.close()
    return render_template("index.html", songs=songs, liked_ids=[])

# ================= LIKE =================
@app.route('/like/<int:id>')
def like(id):
    conn = get_db()
    conn.execute("INSERT INTO likes(username, song_id) VALUES (?,?)", ("guest", id))
    conn.commit()
    conn.close()
    return redirect('/')

# ================= SEARCH =================
@app.route('/search')
def search():
    q = request.args.get("q")

    conn = get_db()
    songs = conn.execute("SELECT * FROM songs WHERE name LIKE ?",('%'+q+'%',)).fetchall()
    conn.close()

    return render_template("index.html", songs=songs, liked_ids=[])

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)