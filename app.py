from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB limit

def get_db():
    conn = sqlite3.connect("song.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS songs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        file TEXT,
        image TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS likes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_id INTEGER
    )""")
    conn.commit(); conn.close()

init_db()

@app.route('/')
def home():
    conn = get_db()
    songs = conn.execute("SELECT * FROM songs").fetchall()
    liked = conn.execute("SELECT song_id FROM likes").fetchall()
    liked_ids = [l["song_id"] for l in liked]
    conn.close()
    return render_template("index.html", songs=songs, liked_ids=liked_ids)

@app.route('/upload', methods=["GET","POST"])
def upload():
    if request.method == "POST":
        # ---- DEBUG PRINTS (Render logs में दिखेंगे) ----
        print("FORM KEYS:", list(request.form.keys()))
        print("FILES KEYS:", list(request.files.keys()))

        image = request.files.get("image")
        songs = request.files.getlist("songs")

        print("IMAGE:", image.filename if image else "None")
        print("SONGS COUNT:", len(songs))

        # folders ensure
        os.makedirs("static/songs", exist_ok=True)
        os.makedirs("static/images", exist_ok=True)

        # save image (optional)
        image_path = ""
        if image and image.filename:
            image_path = os.path.join("static/images", image.filename)
            image.save(image_path)
            print("IMAGE SAVED:", image_path)

        conn = get_db()
        inserted = 0

        for s in songs:
            if not s or not s.filename:
                continue

            # simple safe filename
            filename = s.filename.replace(" ", "_")
            song_path = os.path.join("static/songs", filename)

            s.save(song_path)
            name = os.path.splitext(filename)[0]

            conn.execute(
                "INSERT INTO songs(name,file,image) VALUES (?,?,?)",
                (name, song_path, image_path)
            )
            inserted += 1
            print("SAVED:", song_path)

        conn.commit(); conn.close()
        print("INSERTED COUNT:", inserted)

        return redirect(url_for('home'))

    return render_template("upload.html")

@app.route('/like/<int:song_id>')
def like(song_id):
    conn = get_db()
    exist = conn.execute("SELECT 1 FROM likes WHERE song_id=?", (song_id,)).fetchone()
    if exist:
        conn.execute("DELETE FROM likes WHERE song_id=?", (song_id,))
    else:
        conn.execute("INSERT INTO likes(song_id) VALUES (?)", (song_id,))
    conn.commit(); conn.close()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)