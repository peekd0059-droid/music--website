from flask import Flask, render_template, request, redirect
import sqlite3, os

app = Flask(__name__)

# ===== DB =====
def get_db():
    conn = sqlite3.connect("song.db")
    conn.row_factory = sqlite3.Row
    return conn

# ===== INIT DB =====
def init_db():
    conn = get_db()
    c = conn.cursor()

    # songs table
    c.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        file TEXT,
        image TEXT
    )
    """)

    # likes table
    c.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ===== ADMIN FLAG =====
@app.context_processor
def inject_admin():
    return dict(is_admin=True)

# ===== HOME =====
@app.route('/')
def home():
    conn = get_db()
    songs = conn.execute("SELECT * FROM songs").fetchall()

    song_data = []
    for s in songs:
        count = conn.execute(
            "SELECT COUNT(*) FROM likes WHERE song_id=?",
            (s["id"],)
        ).fetchone()[0]

        song_data.append({
            "id": s["id"],
            "name": s["name"],
            "file": s["file"],
            "image": s["image"],
            "likes": count
        })

    conn.close()
    return render_template("index.html", songs=song_data)

# ===== UPLOAD =====
@app.route('/upload', methods=["GET","POST"])
def upload():

    is_admin = True
    if not is_admin:
        return "Access Denied"

    if request.method == "POST":

        image = request.files.get("image")
        songs = request.files.getlist("songs")

        os.makedirs("static/songs", exist_ok=True)
        os.makedirs("static/images", exist_ok=True)

        image_path = ""

        if image and image.filename:
            image_path = "images/" + image.filename
            image.save(os.path.join("static", image_path))

        conn = get_db()

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