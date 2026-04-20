from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os

app = Flask(__name__)

# DB
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

# Home
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

# ❤️ Like API
@app.route("/like", methods=["POST"])
def like_song():
    data = request.json

    cursor.execute(
        "INSERT INTO liked_songs (name, file, image) VALUES (?, ?, ?)",
        (data["name"], data["file"], data["image"])
    )
    conn.commit()

    return jsonify({"status": "ok"})

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
    app.run()