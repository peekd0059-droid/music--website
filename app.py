from flask import Flask, render_template, request, redirect, session
import sqlite3
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "supersecretkey"


# CLOUDINARY CONFIG (👉 replace with your keys)
cloudinary.config(
    cloud_name="YOUR_CLOUD_NAME",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET"
)


# DB
def get_db():
    return sqlite3.connect("song.db")


# INIT DB
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

    conn.commit()
    conn.close()


init_db()


# ================= ADMIN =================

ADMIN_USER = "admin"
ADMIN_PASS = "123"


@app.route('/admin', methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USER and request.form["password"] == ADMIN_PASS:
            session["admin"] = True
            return redirect('/upload')

    return render_template("admin_login.html")


# ================= UPLOAD (CLOUD) =================

@app.route('/upload', methods=["GET", "POST"])
def upload():
    if not session.get("admin"):
        return redirect('/admin')

    if request.method == "POST":
        name = request.form["name"]
        song = request.files["song"]
        image = request.files["image"]

        # UPLOAD TO CLOUD
        song_upload = cloudinary.uploader.upload(song, resource_type="video")
        image_upload = cloudinary.uploader.upload(image)

        song_url = song_upload["secure_url"]
        image_url = image_upload["secure_url"]

        # SAVE IN DB
        conn = get_db()
        c = conn.cursor()

        c.execute("INSERT INTO songs (name,file,image) VALUES (?,?,?)",
                  (name, song_url, image_url))

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("upload.html")


# ================= HOME =================

@app.route('/')
def home():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM songs")
    songs = c.fetchall()

    conn.close()

    return render_template("index.html", songs=songs)


# ================= PLAYER =================

if __name__ == "__main__":
    app.run(debug=True)