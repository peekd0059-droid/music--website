from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    conn = sqlite3.connect("songs.db")
    conn.row_factory = sqlite3.Row
    return conn

# ===== DATABASE INIT =====
def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        file TEXT,
        image TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS liked_songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        name TEXT,
        file TEXT,
        image TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        name TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS playlist_songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id INTEGER,
        name TEXT,
        file TEXT,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ===== HOME =====
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()

    try:
        c.execute("SELECT * FROM songs")
        data = c.fetchall()
    except:
        data = []

    songs = []
    for row in data:
        songs.append({
            "name": row["name"],
            "file": row["file"],
            "image": row["image"]
        })

    conn.close()
    return render_template("index.html", songs=songs)

# ===== SIGNUP =====
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")

# ===== LOGIN =====
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        conn.close()

        if user:
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid Login"

    return render_template("login.html")

# ===== LOGOUT =====
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ===== LIKE =====
@app.route("/like", methods=["POST"])
def like_song():
    if "user" not in session:
        return "Login required"

    data = request.get_json()

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    INSERT INTO liked_songs (user, name, file, image)
    VALUES (?, ?, ?, ?)
    """, (session["user"], data["name"], data["file"], data["image"]))

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})

# ===== LIKED PAGE =====
@app.route("/liked")
def liked():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()

    try:
        c.execute("SELECT * FROM liked_songs WHERE user=?", (session["user"],))
        data = c.fetchall()
    except:
        data = []

    songs = []
    for row in data:
        songs.append({
            "name": row["name"],
            "file": row["file"],
            "image": row["image"]
        })

    conn.close()
    return render_template("liked.html", songs=songs)

# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)
