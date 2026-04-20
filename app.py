from flask import Flask, render_template, request, jsonify, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("songs.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create tables
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
CREATE TABLE IF NOT EXISTS liked_songs (
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
    name TEXT,
    file TEXT,
    image TEXT
)
""")

conn.commit()
conn.close()

# Home
@app.route("/")
def home():
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

# ❤️ Like
@app.route("/like", methods=["POST"])
def like_song():
    data = request.get_json()

    conn = get_db()
    c = conn.cursor()

    c.execute(
        "INSERT INTO liked_songs (name, file, image) VALUES (?, ?, ?)",
        (data["name"], data["file"], data["image"])
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# ❤️ Liked Page
@app.route("/liked")
def liked():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM liked_songs")
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

# 🎵 Create Playlist
@app.route("/create_playlist", methods=["POST"])
def create_playlist():
    name = request.form["name"]

    conn = get_db()
    c = conn.cursor()

    c.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

    return redirect("/")

# ➕ Add to Playlist
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

# 📂 View Playlist
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

if __name__ == "__main__":
    app.run(debug=True)
