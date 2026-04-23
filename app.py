from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# ================= DB =================
def get_db():
    conn = sqlite3.connect("song.db")
    conn.row_factory = sqlite3.Row
    return conn

# ================= INIT =================
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
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    c.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= PLAYLIST =================
def get_playlists():
    conn = get_db()
    playlists = conn.execute("SELECT * FROM playlists").fetchall()
    conn.close()
    return playlists

# ================= HOME =================
@app.route('/')
def home():
    conn = get_db()
    songs = conn.execute("SELECT * FROM songs").fetchall()
    liked = conn.execute("SELECT song_id FROM likes").fetchall()

    liked_ids = [l["song_id"] for l in liked]

    conn.close()

    return render_template("index.html",
                           songs=songs,
                           playlists=get_playlists(),
                           liked_ids=liked_ids)

# ================= BULK UPLOAD =================
@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == "POST":

        image = request.files["image"]
        songs = request.files.getlist("songs")

        # ensure folders
        os.makedirs("static/songs", exist_ok=True)
        os.makedirs("static/images", exist_ok=True)

        # save image once
        image_path = "static/images/" + image.filename
        image.save(image_path)

        conn = get_db()

        for song in songs:
            if song.filename == "":
                continue

            song_path = "static/songs/" + song.filename
            song.save(song_path)

            name = os.path.splitext(song.filename)[0]

            conn.execute(
                "INSERT INTO songs(name,file,image) VALUES (?,?,?)",
                (name, song_path, image_path)
            )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("upload.html")

# ================= LIKE =================
@app.route('/like/<int:song_id>')
def like(song_id):
    conn = get_db()

    exist = conn.execute(
        "SELECT * FROM likes WHERE song_id=?", (song_id,)
    ).fetchone()

    if exist:
        conn.execute("DELETE FROM likes WHERE song_id=?", (song_id,))
    else:
        conn.execute("INSERT INTO likes(song_id) VALUES (?)", (song_id,))

    conn.commit()
    conn.close()

    return redirect('/')

# ================= LIKED PAGE =================
@app.route('/liked')
def liked():
    conn = get_db()

    songs = conn.execute("""
    SELECT songs.* FROM songs
    JOIN likes ON songs.id = likes.song_id
    """).fetchall()

    conn.close()

    return render_template("index.html",
                           songs=songs,
                           playlists=get_playlists(),
                           liked_ids=[s["id"] for s in songs])

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)