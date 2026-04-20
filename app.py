from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Database connection
conn = sqlite3.connect("songs.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables
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


# Home route
@app.route("/")
def home():
    cursor.execute("SELECT * FROM songs")
    data = cursor.fetchall()

    songs = []
    for row in data:
        songs.append({
            "name": row[1],
            "file": row[2],
            "image": row[3]
        })

    return render_template("index.html", songs=songs)


# ❤️ Like route (FIXED)
@app.route("/like", methods=["POST"])
def like_song():
    try:
        data = request.get_json()

        name = data.get("name")
        file = data.get("file")
        image = data.get("image")

        cursor.execute(
            "INSERT INTO liked_songs (name, file, image) VALUES (?, ?, ?)",
            (name, file, image)
        )
        conn.commit()

        return jsonify({"status": "success"})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"status": "error"})


# ❤️ Liked page
@app.route("/liked")
def liked():
    cursor.execute("SELECT * FROM liked_songs")
    data = cursor.fetchall()

    songs = []
    for row in data:
        songs.append({
            "name": row[1],
            "file": row[2],
            "image": row[3]
        })

    return render_template("liked.html", songs=songs)


if __name__ == "__main__":
    app.run(debug=True)