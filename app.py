from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ================= DB =================
def get_db():
    conn = sqlite3.connect("song.db")
    conn.row_factory = sqlite3.Row
    return conn

# ================= INIT =================
def init_db():
    conn = get_db()
    c = conn.cursor()

    # songs
    c.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        file TEXT,
        image TEXT
    )
    """)

    # playlists
    c.execute("""
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    # playlist songs
    c.execute("""
    CREATE TABLE IF NOT EXISTS playlist_songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id INTEGER,
        song_id INTEGER
    )
    """)

    # moods
    c.execute("""
    CREATE TABLE IF NOT EXISTS moods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_id INTEGER,
        mood TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= GET PLAYLISTS =================
def get_playlists():
    conn = get_db()
    playlists = conn.execute("SELECT * FROM playlists").fetchall()
    conn.close()
    return playlists

# ================= HOME =================
@app.route('/')
def home():
    conn = get_db()
    songs = conn.execute("SELECT * FROM songs").fetchall()
    conn.close()

    return render_template("index.html", songs=songs, playlists=get_playlists())

# ================= CREATE PLAYLIST =================
@app.route('/create_playlist', methods=["POST"])
def create_playlist():
    name = request.form["name"]

    conn = get_db()
    conn.execute("INSERT INTO playlists(name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

    return redirect('/')

# ================= ADD SONG =================
@app.route('/add_to_playlist/<int:song_id>', methods=["POST"])
def add_to_playlist(song_id):
    playlist_id = request.form["playlist_id"]

    conn = get_db()
    conn.execute(
        "INSERT INTO playlist_songs(playlist_id, song_id) VALUES (?,?)",
        (playlist_id, song_id)
    )
    conn.commit()
    conn.close()

    return redirect('/')

# ================= VIEW PLAYLIST =================
@app.route('/playlist/<int:id>')
def view_playlist(id):
    conn = get_db()

    songs = conn.execute("""
    SELECT songs.* FROM songs
    JOIN playlist_songs ON songs.id = playlist_songs.song_id
    WHERE playlist_songs.playlist_id = ?
    """, (id,)).fetchall()

    conn.close()

    return render_template("index.html", songs=songs, playlists=get_playlists())

# ================= 🎯 MOOD SYSTEM =================
@app.route('/mood')
def mood():
    mood = request.args.get("type", "")

    conn = get_db()

    songs = conn.execute("""
    SELECT songs.* FROM songs
    JOIN moods ON songs.id = moods.song_id
    WHERE moods.mood = ?
    """, (mood,)).fetchall()

    conn.close()

    return render_template("index.html", songs=songs, playlists=get_playlists())

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)