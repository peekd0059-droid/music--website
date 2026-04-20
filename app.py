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

    # GET LIKED SONG IDS
    c.execute("SELECT song_id FROM likes WHERE username=?", (username,))
    liked = c.fetchall()
    liked_ids = [i[0] for i in liked]

    conn.close()

    return render_template("index.html", songs=songs, liked_ids=liked_ids)


# SEARCH
@app.route('/search')
def search():
    query = request.args.get("q")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM songs WHERE name LIKE ?", ('%' + query + '%',))
    songs = c.fetchall()

    username = session.get("user", "guest")

    c.execute("SELECT song_id FROM likes WHERE username=?", (username,))
    liked = c.fetchall()
    liked_ids = [i[0] for i in liked]

    conn.close()

    return render_template("index.html", songs=songs, liked_ids=liked_ids)


# ❤️ LIKE TOGGLE
@app.route('/like/<int:song_id>')
def like(song_id):
    username = session.get("user", "guest")

    conn = get_db()
    c = conn.cursor()

    # CHECK EXIST
    c.execute("SELECT * FROM likes WHERE username=? AND song_id=?", (username, song_id))
    existing = c.fetchone()

    if existing:
        # UNLIKE
        c.execute("DELETE FROM likes WHERE username=? AND song_id=?", (username, song_id))
    else:
        # LIKE
        c.execute("INSERT INTO likes (username, song_id) VALUES (?, ?)", (username, song_id))

    conn.commit()
    conn.close()

    return redirect('/')


# ❤️ LIKED PAGE
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

    conn.close()

    return render_template("index.html", songs=songs, liked_ids=liked_ids)


# PLAYLIST
@app.route('/create_playlist', methods=["POST"])
def create_playlist():
    name = request.form["name"]
    username = session.get("user", "guest")

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO playlists (username,name) VALUES (?,?)", (username, name))
    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/playlist')
def playlist():
    username = session.get("user", "guest")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM playlists WHERE username=?", (username,))
    playlists = c.fetchall()
    conn.close()

    return render_template("playlist.html", playlists=playlists)


if __name__ == "__main__":
    app.run(debug=True)