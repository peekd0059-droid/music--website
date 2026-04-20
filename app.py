from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

DB = "songs.db"

def get_db():
    return sqlite3.connect(DB)

# ===== INIT DB =====
def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY,
        name TEXT,
        file TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ===== INSERT DEFAULT SONGS =====
def insert_default_songs():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM songs")
    count = c.fetchone()[0]

    if count == 0:
        c.execute("INSERT INTO songs (name, file) VALUES (?, ?)",
                  ("DR MOB Fearless Funk", "songs/drmob.mp3"))

        c.execute("INSERT INTO songs (name, file) VALUES (?, ?)",
                  ("MXZI Deno Favela", "songs/mxzi.mp3"))

    conn.commit()
    conn.close()

insert_default_songs()

# ===== HOME =====
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM songs")
    data = c.fetchall()
    conn.close()

    songs = []

    for s in data:
        # 🔥 IMAGE AUTO MATCH
        if "DR MOB" in s[1]:
            img = "images/drmob.jpg"
        else:
            img = "images/mxzi.jpg"

        songs.append({
            "name": s[1],
            "file": s[2],
            "img": img
        })

    return render_template("index.html", songs=songs)

# ===== LOGIN =====
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = u
            return redirect("/")
        else:
            return "Wrong username or password"

    return render_template("login.html")

# ===== SIGNUP =====
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (NULL, ?, ?)", (u, p))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")

# ===== LOGOUT =====
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)