from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    return sqlite3.connect("song.db")


# HOME
@app.route('/')
def home():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM songs")
    songs = c.fetchall()
    conn.close()
    return render_template("index.html", songs=songs)


# LOGIN
@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect('/')
        else:
            return "Wrong Login"

    return render_template("login.html")


# SIGNUP
@app.route('/signup', methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,password))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template("signup.html")


# LOGOUT
@app.route('/logout')
def logout():
    session.pop("user",None)
    return redirect('/')


# 🔥 LIKE SONG
@app.route('/like/<int:song_id>')
def like(song_id):
    username = session.get("user","guest")

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO likes (username, song_id) VALUES (?,?)",(username,song_id))
    conn.commit()
    conn.close()

    return redirect('/')


# 🔥 LIKED PAGE
@app.route('/liked')
def liked():
    username = session.get("user","guest")

    conn = get_db()
    c = conn.cursor()
    c.execute("""
    SELECT songs.* FROM songs
    JOIN likes ON songs.id = likes.song_id
    WHERE likes.username=?
    """,(username,))
    songs = c.fetchall()
    conn.close()

    return render_template("index.html", songs=songs)


# 🔥 SEARCH
@app.route('/search')
def search():
    query = request.args.get("q")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM songs WHERE name LIKE ?",('%'+query+'%',))
    songs = c.fetchall()
    conn.close()

    return render_template("index.html", songs=songs)


# 🔥 CREATE PLAYLIST
@app.route('/create_playlist', methods=["POST"])
def create_playlist():
    name = request.form["name"]
    username = session.get("user","guest")

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO playlists (username,name) VALUES (?,?)",(username,name))
    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)