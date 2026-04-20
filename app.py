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

    # users
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # liked songs
    c.execute("""
    CREATE TABLE IF NOT EXISTS liked (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        song TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ===== HOME (Spotify UI) =====
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    songs = [
        {"name": "DR MOB Fearless Funk", "file": "songs/DR MØB, Chris Linton - Fearless Funk.mp3", "img": "images/DR MØB, Chris Linton - Fearless Funk.jpg"},
        {"name": "MXZI Deno Favela", "file": "songs/MXZI, Deno - FAVELA.mp3", "img": "images/MXZI, Deno - FAVELA.jpg"},
    ]

    return render_template("index.html", songs=songs)


# ===== LIKE SONG =====
@app.route("/like/<song>")
def like(song):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()

    c.execute("INSERT INTO liked (username, song) VALUES (?, ?)", (session["user"], song))

    conn.commit()
    conn.close()

    return redirect("/")


# ===== LIKED PAGE =====
@app.route("/liked")
def liked():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT song FROM liked WHERE username=?", (session["user"],))
    songs = c.fetchall()

    conn.close()

    return render_template("liked.html", songs=songs)


# ===== SIGNUP =====
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect("/login")

    return render_template("signup.html")


# ===== LOGIN =====
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        conn.close()

        if user:
            session["user"] = username
            return redirect("/")
        else:
            return "Wrong username or password"

    return render_template("login.html")


# ===== LOGOUT =====
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
