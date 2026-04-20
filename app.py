from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    conn = sqlite3.connect("songs.db")
    conn.row_factory = sqlite3.Row
    return conn

# ================= DATABASE =================
conn = get_db()
c = conn.cursor()

# Songs
c.execute("""
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    file TEXT,
    image TEXT
)
""")

# Users
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# ❤️ User-wise liked songs
c.execute("""
CREATE TABLE IF NOT EXISTS liked_songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    name TEXT,
    file TEXT,
    image TEXT
)
""")

# Playlist
c.execute("""
CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    name TEXT
)
""")

# Playlist songs
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

# ================= HOME =================
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM songs")
    data = c.fetchall()

    songs = []
    for row in data:
        songs.append({
            "name": row["name"],
            "file": row["file"],
            "image": row["image"]
        })

    conn.close()
    return render_template("index.html", songs=songs)

# ================= SIGNUP =================
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

# ================= LOGIN =================
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

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ================= ❤️ LIKE =================
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

# ================= ❤️ LIKED PAGE =================
@app.route("/liked")
def liked():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM liked_songs WHERE user=?", (session["user"],))
    data = c.fetchall()

    songs = []
    for row in data:
        songs.append({
            "name": row["name"],
            "file": row["file"],
            "image": row["image"]
        })

    conn.close()
    return render_template("liked.html", songs=songs)

# ================= 📂 CREATE PLAYLIST =================
@app.route("/create_playlist", methods=["POST"])
def create_playlist():
    name = request.form["name"]

    conn = get_db()
    c = conn.cursor()

    c.execute("INSERT INTO playlists (user, name) VALUES (?, ?)", (session["user"], name))
    conn.commit()
    conn.close()

    return redirect("/")

# ================= ➕ ADD TO PLAYLIST =================
@app.route("/add_to_playlist", methods=["POST"])
def add_to_playlist():
    data = request.get_json()

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    INSERT INTO playlist_songs (playlist_id, name, file, image)
    VALUES (?, ?, ?, ?)
    """, (data["playlist_id"], data["name"], data["file"], data["image"]))

    conn.commit()
    conn.close()

    return "OK"

# ================= VIEW PLAYLIST =================
@app.route("/playlist/<int:id>")
def view_playlist(id):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT name FROM playlists WHERE id=?", (id,))
    playlist = c.fetchone()

    c.execute("SELECT name, file, image FROM playlist_songs WHERE playlist_id=?", (id,))
    songs = c.fetchall()

    conn.close()

    return render_template("playlist.html", playlist=playlist, songs=songs)

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
