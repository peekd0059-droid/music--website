from flask import Flask, render_template, request, redirect, session
from utils.db import get_db

app = Flask(__name__)
app.secret_key = "secret123"


# HOME
@app.route('/')
def home():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM songs")
    songs = c.fetchall()

    username = session.get("user", "guest")

    # liked
    try:
        c.execute("SELECT song_id FROM likes WHERE username=?", (username,))
        liked = c.fetchall()
        liked_ids = [i[0] for i in liked]
    except:
        liked_ids = []

    # playlists
    try:
        c.execute("SELECT * FROM playlists WHERE username=?", (username,))
        playlists = c.fetchall()
    except:
        playlists = []

    conn.close()

    return render_template("index.html", songs=songs, liked_ids=liked_ids, playlists=playlists)


# SEARCH
@app.route('/search')
def search():
    query = request.args.get("q", "")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM songs WHERE name LIKE ?", ('%' + query + '%',))
    songs = c.fetchall()

    username = session.get("user", "guest")

    c.execute("SELECT song_id FROM likes WHERE username=?", (username,))
    liked = c.fetchall()
    liked_ids = [i[0] for i in liked]

    c.execute("SELECT * FROM playlists WHERE username=?", (username,))
    playlists = c.fetchall()

    conn.close()

    return render_template("index.html", songs=songs, liked_ids=liked_ids, playlists=playlists)


# LIKE TOGGLE
@app.route('/like/<int:song_id>')
def like(song_id):
    username = session.get("user", "guest")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM likes WHERE username=? AND song_id=?", (username, song_id))
    existing = c.fetchone()

    if existing:
        c.execute("DELETE FROM likes WHERE username=? AND song_id=?", (username, song_id))
    else:
        c.execute("INSERT INTO likes (username, song_id) VALUES (?, ?)", (username, song_id))

    conn.commit()
    conn.close()

    return redirect('/')


# LIKED PAGE
@app.route('/liked')
def liked():
    username = session.get("user", "guest")

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    SELECT songs.* FROM songs
    JOIN likes ON songs.id = likes.song_id
    WHERE likes.username=?
    """, (username,))
    songs = c.fetchall()

    liked_ids = [s[0] for s in songs]

    c.execute("SELECT * FROM playlists WHERE username=?", (username,))
    playlists = c.fetchall()

    conn.close()

    return render_template("index.html", songs=songs, liked_ids=liked_ids, playlists=playlists)


# CREATE PLAYLIST
@app.route('/create_playlist', methods=["POST"])
def create_playlist():
    name = request.form.get("name")
    username = session.get("user", "guest")

    conn = get_db()
    c = conn.cursor()

    c.execute("INSERT INTO playlists (username,name) VALUES (?,?)", (username, name))

    conn.commit()
    conn.close()

    return redirect('/')


# ADD SONG TO PLAYLIST
@app.route('/add_to_playlist/<int:song_id>', methods=["POST"])
def add_to_playlist(song_id):
    playlist_id = request.form.get("playlist_id")

    conn = get_db()
    c = conn.cursor()

    c.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES (?,?)",
              (playlist_id, song_id))

    conn.commit()
    conn.close()

    return redirect('/')


# PLAYLIST PAGE
@app.route('/playlist')
def playlist():
    username = session.get("user", "guest")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM playlists WHERE username=?", (username,))
    playlists = c.fetchall()

    conn.close()

    return render_template("playlist.html", playlists=playlists)


# PLAYLIST DETAIL
@app.route('/playlist/<int:pid>')
def playlist_detail(pid):
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    SELECT songs.* FROM songs
    JOIN playlist_songs ON songs.id = playlist_songs.song_id
    WHERE playlist_songs.playlist_id=?
    """, (pid,))

    songs = c.fetchall()

    conn.close()

    return render_template("index.html", songs=songs, liked_ids=[], playlists=[])


if __name__ == "__main__":
    app.run(debug=True)