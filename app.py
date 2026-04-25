from flask import Flask, render_template, request, redirect
import sqlite3
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# ===== CLOUDINARY CONFIG =====
cloudinary.config(
    cloud_name="dyyhnehhj",
    api_key="241782544424174",
    api_secret="kAwAs7J5k8aKx85jaO5N19MRc8E"
)

# ===== DB =====
def get_db():
    conn = sqlite3.connect("song.db")
    conn.row_factory = sqlite3.Row
    return conn

# ===== INIT DB =====
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
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ===== ADMIN =====
@app.context_processor
def inject_admin():
    return dict(is_admin=True)

# ===== HOME =====
@app.route('/')
def home():
    conn = get_db()
    songs = conn.execute("SELECT * FROM songs").fetchall()

    data = []
    for s in songs:
        count = conn.execute(
            "SELECT COUNT(*) FROM likes WHERE song_id=?",
            (s["id"],)
        ).fetchone()[0]

        data.append({
            "id": s["id"],
            "name": s["name"],
            "file": s["file"],
            "image": s["image"],
            "likes": count
        })

    conn.close()
    return render_template("index.html", songs=data)

# ===== UPLOAD (CLOUD) =====
@app.route('/upload', methods=["GET","POST"])
def upload():

    if request.method == "POST":

        image = request.files.get("image")
        songs = request.files.getlist("songs")

        image_url = ""

        # ===== IMAGE UPLOAD =====
        if image:
            result = cloudinary.uploader.upload(image)
            image_url = result["secure_url"]

        conn = get_db()

        # ===== SONG UPLOAD =====
        for s in songs:
            if s.filename == "":
                continue

            result = cloudinary.uploader.upload(
                s,
                resource_type="video"  # 🔥 important for mp3
            )

            song_url = result["secure_url"]

            name = s.filename.split(".")[0]

            conn.execute(
                "INSERT INTO songs(name,file,image) VALUES (?,?,?)",
                (name, song_url, image_url)
            )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("upload.html")

# ===== LIKE =====
@app.route('/like/<int:id>')
def like(id):
    conn = get_db()

    existing = conn.execute(
        "SELECT * FROM likes WHERE song_id=?",
        (id,)
    ).fetchone()

    if existing:
        conn.execute("DELETE FROM likes WHERE song_id=?", (id,))
    else:
        conn.execute("INSERT INTO likes(song_id) VALUES (?)", (id,))

    conn.commit()
    conn.close()

    return redirect('/')

# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)