from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import hashlib
import os

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

# ================= AUTH =================

@app.route('/signup', methods=["GET","POST"])
def signup():
    if request.method == "POST":
        u = request.form["username"]
        p = hash_password(request.form["password"])

        conn = get_db()
        try:
            conn.execute("INSERT INTO users(username,password) VALUES (?,?)",(u,p))
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect('/login')

    return render_template("signup.html")

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = hash_password(request.form["password"])

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p)).fetchone()

        if user:
            session["user"] = u
            return redirect('/')

        return "Wrong login"

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ================= HOME =================

@app.route('/')
def home():
    conn = get_db()

    songs = conn.execute("SELECT * FROM songs").fetchall()

    user = session.get("user", "")
    liked = [i["song_id"] for i in conn.execute("SELECT song_id FROM likes WHERE username=?",(user,))]

    conn.close()

    return render_template("index.html", songs=songs, liked_ids=liked)

# ================= LIKE =================

@app.route('/like/<int:id>')
def like(id):
    user = session.get("user", "")

    conn = get_db()
    c = conn.cursor()

    existing = c.execute("SELECT * FROM likes WHERE username=? AND song_id=?",(user,id)).fetchone()

    if existing:
        c.execute("DELETE FROM likes WHERE username=? AND song_id=?",(user,id))
    else:
        c.execute("INSERT INTO likes(username,song_id) VALUES (?,?)",(user,id))

    conn.commit()
    conn.close()

    return redirect('/')

# ================= PLAY =================

@app.route('/play/<int:id>')
def play(id):
    conn = get_db()
    conn.execute("UPDATE songs SET plays = plays + 1 WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return ""

# ================= SEARCH =================

@app.route('/search')
def search():
    q = request.args.get("q")

    conn = get_db()
    songs = conn.execute("SELECT * FROM songs WHERE name LIKE ?",('%'+q+'%',)).fetchall()
    conn.close()

    return render_template("index.html", songs=songs, liked_ids=[])

# ================= UPLOAD =================

@app.route('/upload', methods=["GET","POST"])
def upload():
    if request.method == "POST":
        name = request.form["name"]
        song = request.files["song"]
        image = request.files["image"]

        song_path = "static/songs/" + song.filename
        image_path = "static/images/" + image.filename

        song.save(song_path)
        image.save(image_path)

        conn = get_db()
        conn.execute("INSERT INTO songs(name,file,image) VALUES (?,?,?)",
                     (name, song_path, image_path))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("upload.html")

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)