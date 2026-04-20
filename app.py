from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("songs.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create tables
conn = get_db()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    file TEXT,
    image TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS liked_songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM songs")
    data = cursor.fetchall()

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
    try:
        data = request.get_json()

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO liked_songs (name, file, image) VALUES (?, ?, ?)",
            (data["name"], data["file"], data["image"])
        )

        conn.commit()
        conn.close()

        return jsonify({"status": "success"})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"status": "error"})


# ❤️ Liked page
@app.route("/liked")
def liked():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM liked_songs")
    data = cursor.fetchall()

    songs = []
    for row in data:
        songs.append({
            "name": row["name"],
            "file": row["file"],
            "image": row["image"]
        })

    conn.close()
    return render_template("liked.html", songs=songs)


if __name__ == "__main__":
    app.run(debug=True)
