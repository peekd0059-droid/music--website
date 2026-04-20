from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"


# DB
def get_db():
    return sqlite3.connect("song.db")


# AUTO DB INIT
def init_db():
    conn = sqlite3.connect("song.db")
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
    CREATE TABLE IF NOT EXISTS likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    song_id INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    name TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS playlist_songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id INTEGER,
    song_id INTEGER
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ADMIN LOGIN
ADMIN_USER = "admin"
ADMIN_PASS = "123"


@app.route('/admin', methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        if user == ADMIN_USER and pwd == ADMIN_PASS:
            session["admin"] = True
            return redirect('/upload')
        else:
            return "Wrong Admin Login"

    return render_template("admin_login.html")


# UPLOAD
@app.route('/upload', methods=["GET", "POST"])
def upload():
    if not session.get("admin"):
        return redirect('/admin')

    if request.method == "POST":
        name = request.form["name"]
        song = request.files["song"]
        image = request.files["image"]

        song_path = "songs/" + song.filename
        image_path = "images/" + image.filename

        song.save(os.path.join("static", song_path))
        image.save(os.path.join("static", image_path))

        conn = get_db()
        c = conn.cursor()

        c.execute("INSERT INTO songs (name,file,image) VALUES (?,?,?)",
                  (name, song_path, image_path))

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("upload.html")


# HOME
@app.route('/')
def home():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM songs")
    songs = c.fetchall()

    username = session.get("user", "guest")

    c.execute("SELECT song_id FROM likes WHERE username=?", (username,))
    liked = c.fetchall()
    liked_ids = [i[0] for i in liked]

    c.execute("SELECT * FROM playlists WHERE username=?", (username,))
    playlists = c.fetchall()

    conn.close()

    return render_template("index.html", songs=songs, liked_ids=liked_ids, playlists=playlists)


# SEARCH
@app.route('/search')
def search():
    query = request.args.get("q", "")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM songs WHERE name LIKE ?", ('%' + query + '%',))
    songs = c.fetchall()

    username = session.get("user", "guest")

    c.execute("SELECT song_id FROM likes WHERE username=?", (username,))
    liked = c.fetchall()
    liked_ids = [i[0] for i in liked]

    c.execute("SELECT * FROM playlists WHERE username=?", (username,))
    playlists = c.fetchall()

    conn.close()

    return render_template("index.html", songs=songs, liked_ids=liked_ids, playlists=playlists)


# LIKE TOGGLE
@app.route('/like/<int:song_id>')
def like(song_id):
    username = session.get("user", "guest")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM likes WHERE username=? AND song_id=?", (username, song_id))
    existing = c.fetchone()

    if existing:
        c.execute("DELETE FROM likes WHERE username=? AND song_id=?", (username, song_id))
    else:
        c.execute("INSERT INTO likes (username, song_id) VALUES (?, ?)", (username, song_id))

    conn.commit()
    conn.close()

    return redirect('/')


# CREATE PLAYLIST
@app.route('/create_playlist', methods=["POST"])
def create_playlist():
    name = request.form["name"]
    username = session.get("user", "guest")

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO playlists (username,name) VALUES (?,?)", (username, name))

    conn.commit()
    conn.close()

    return redirect('/')


# ADD SONG TO PLAYLIST
@app.route('/add_to_playlist/<int:song_id>', methods=["POST"])
def add_to_playlist(song_id):
    playlist_id = request.form["playlist_id"]

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?,?)",
              (playlist_id, song_id))

    conn.commit()
    conn.close()

    return redirect('/')


# PLAYLIST PAGE
@app.route('/playlist')
def playlist():
    username = session.get("user", "guest")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM playlists WHERE username=?", (username,))
    playlists = c.fetchall()

    conn.close()

    return render_template("playlist.html", playlists=playlists)


# PLAYLIST DETAIL
@app.route('/playlist/<int:pid>')
def playlist_detail(pid):
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    SELECT songs.* FROM songs
    JOIN playlist_songs ON songs.id = playlist_songs.song_id
    WHERE playlist_songs.playlist_id=?
    """, (pid,))

    songs = c.fetchall()

    conn.close()

    return render_template("index.html", songs=songs, liked_ids=[], playlists=[])


if __name__ == "__main__":
    app.run(debug=True)