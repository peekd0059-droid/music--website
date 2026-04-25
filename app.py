from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("song.db")
    conn.row_factory = sqlite3.Row
    return conn

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

    conn.commit()
    conn.close()

init_db()

# HOME
@app.route('/')
def home():
    conn = get_db()
    songs = conn.execute("SELECT * FROM songs").fetchall()
    conn.close()
    return render_template("index.html", songs=songs)

# UPLOAD
@app.route('/upload', methods=["GET","POST"])
def upload():
    if request.method == "POST":

        image = request.files.get("image")
        songs = request.files.getlist("songs")

        os.makedirs("static/songs", exist_ok=True)
        os.makedirs("static/images", exist_ok=True)

        image_path = ""

        # SAVE IMAGE
        if image and image.filename:
            image_path = "images/" + image.filename
            image.save(os.path.join("static", image_path))

        conn = get_db()

        # SAVE SONGS
        for s in songs:
            if s.filename == "":
                continue

            filename = s.filename.replace(" ", "_")

            song_path = "songs/" + filename
            s.save(os.path.join("static", song_path))

            name = filename.split(".")[0]

            conn.execute(
                "INSERT INTO songs(name,file,image) VALUES (?,?,?)",
                (name, song_path, image_path)
            )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)