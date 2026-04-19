from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/songs"
IMAGE_FOLDER = "static/images"

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# DB connection
def get_db():
    conn = sqlite3.connect("songs.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create table if not exists
def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            file TEXT,
            image TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Home page
@app.route("/")
def index():
    conn = get_db()
    songs = conn.execute("SELECT * FROM songs").fetchall()
    conn.close()
    return render_template("index.html", songs=songs)

# Upload (admin use)
@app.route("/upload", methods=["POST"])
def upload():
    song = request.files.get("song")
    image = request.files.get("image")

    if song and image:
        song_filename = song.filename
        image_filename = image.filename

        song.save(os.path.join(UPLOAD_FOLDER, song_filename))
        image.save(os.path.join(IMAGE_FOLDER, image_filename))

        conn = get_db()
        conn.execute(
            "INSERT INTO songs (name, file, image) VALUES (?, ?, ?)",
            (song_filename.split(".")[0], song_filename, image_filename)
        )
        conn.commit()
        conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)