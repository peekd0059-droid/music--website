from flask import Flask, render_template, request, redirect, session, jsonify
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

    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS liked (id INTEGER PRIMARY KEY, username TEXT, song TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS playlist (id INTEGER PRIMARY KEY, username TEXT, name TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS playlist_songs (id INTEGER PRIMARY KEY, playlist_id INTEGER, song TEXT)")

    conn.commit()
    conn.close()

init_db()

# ===== SONG DATA =====
songs_data = [
    {"name": "DR MOB Fearless Funk", "file": "songs/DR MØB, Chris Linton - Fearless Funk.mp3", "img": "images/DR MØB, Chris Linton - Fearless Funk.jpg"},
    {"name": "MXZI Deno Favela", "file": "songs/MXZI, Deno - FAVELA.mp3", "img": "images/MXZI, Deno - FAVELA.jpg"},
]

# ===== HOME =====
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    return render_template("index.html", songs=songs_data)

# ===== CREATE PLAYLIST =====
@app.route("/create_playlist", methods=["POST"])
def create_playlist():
    name = request.form.get("name")

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO playlist VALUES (NULL, ?, ?)", (session["user"], name))
    conn.commit()
    conn.close()

    return redirect("/playlists")

# ===== VIEW PLAYLISTS =====
@app.route("/playlists")
def playlists():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM playlist WHERE username=?", (session["user"],))
    data = c.fetchall()
    conn.close()

    return render_template("playlist.html", playlists=data)

# ===== ADD SONG =====
@app.route("/add_to_playlist", methods=["POST"])
def add_to_playlist():
    pid = request.form.get("pid")
    song = request.form.get("song")

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO playlist_songs VALUES (NULL, ?, ?)", (pid, song))
    conn.commit()
    conn.close()

    return "added"

# ===== LOGIN =====
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = u
            return redirect("/")
        else:
            return "Wrong username/password"

    return render_template("login.html")

# ===== SIGNUP =====
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (NULL, ?, ?)", (u,p))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")

# ===== LOGOUT =====
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)