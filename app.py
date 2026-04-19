from flask import Flask, render_template, request, redirect, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# folders
SONG_FOLDER = "static/songs"
IMAGE_FOLDER = "static/images"

os.makedirs(SONG_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# database
conn = sqlite3.connect("songs.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    file TEXT,
    image TEXT
)
""")
conn.commit()


# 🔄 AUTO DETECT SONGS + IMAGE MATCH
def sync_songs():
    files = os.listdir(SONG_FOLDER)

    cursor.execute("SELECT file FROM songs")
    db_files = [row[0] for row in cursor.fetchall()]

    for file in files:
        if file.endswith(".mp3") and file not in db_files:

            # 🎯 auto clean name
            name = file.replace(".mp3", "").replace("_", " ").replace("-", " ")

            # 🎯 image auto match
            image_name = file.replace(".mp3", ".jpg")

            if not os.path.exists(os.path.join(IMAGE_FOLDER, image_name)):
                image_name = "img4.jpg"  # default image

            cursor.execute(
                "INSERT INTO songs (name, file, image) VALUES (?, ?, ?)",
                (name, file, image_name)
            )
            conn.commit()


# 🔐 ADMIN LOGIN (hidden)
@app.route("/secret-admin-login-123", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["admin"] = True
            return redirect("/")
        return "Wrong credentials ❌"

    return """
    <h2>Admin Login</h2>
    <form method='POST'>
        <input name='username'><br><br>
        <input name='password' type='password'><br><br>
        <button>Login</button>
    </form>
    """


# 🔓 LOGOUT
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")


# 🏠 HOME
@app.route("/", methods=["GET", "POST"])
def home():

    # 🔄 auto sync run
    sync_songs()

    is_admin = session.get("admin")

    # 📤 Upload (only admin + auto name)
    if request.method == "POST":
        if not is_admin:
            return "Unauthorized ❌"

        song = request.files.get("song")
        image = request.files.get("image")

        if song and image:
            filename = song.filename

            name = filename.replace(".mp3", "").replace("_", " ").replace("-", " ")

            song.save(os.path.join(SONG_FOLDER, filename))
            image.save(os.path.join(IMAGE_FOLDER, image.filename))

            cursor.execute(
                "INSERT INTO songs (name, file, image) VALUES (?, ?, ?)",
                (name, filename, image.filename)
            )
            conn.commit()

        return redirect("/")

    # fetch songs
    cursor.execute("SELECT * FROM songs")
    data = cursor.fetchall()

    songs = []
    for row in data:
        songs.append({
            "id": row[0],
            "name": row[1],
            "file": row[2],
            "image": row[3]
        })

    return render_template("index.html", songs=songs, is_admin=is_admin)


# ❌ DELETE (admin only)
@app.route("/delete/<int:id>")
def delete_song(id):

    if not session.get("admin"):
        return "Unauthorized ❌"

    cursor.execute("SELECT file, image FROM songs WHERE id=?", (id,))
    row = cursor.fetchone()

    if row:
        song_path = os.path.join(SONG_FOLDER, row[0])
        image_path = os.path.join(IMAGE_FOLDER, row[1])

        if os.path.exists(song_path):
            os.remove(song_path)

        if os.path.exists(image_path):
            os.remove(image_path)

    cursor.execute("DELETE FROM songs WHERE id=?", (id,))
    conn.commit()

    return redirect("/")


# 🚀 RUN
if __name__ == "__main__":
    app.run(debug=True)