
# ================= TRENDING =================
@app.route('/trending')
def trending():
    conn = get_db()
    songs = conn.execute(
        "SELECT * FROM songs ORDER BY plays DESC LIMIT 10"
    ).fetchall()
    conn.close()

    return render_template("index.html", songs=songs, liked_ids=[])


# ================= SIMPLE AI RECOMMEND =================
@app.route('/recommend')
def recommend():
    user = session.get("user", "")

    conn = get_db()

    liked = conn.execute(
        "SELECT song_id FROM likes WHERE username=?",
        (user,)
    ).fetchall()

    liked_ids = [str(i["song_id"]) for i in liked]

    if liked_ids:
        query = f"""
        SELECT * FROM songs 
        WHERE id NOT IN ({','.join(liked_ids)})
        ORDER BY RANDOM() LIMIT 5
        """
    else:
        query = "SELECT * FROM songs ORDER BY RANDOM() LIMIT 5"

    songs = conn.execute(query).fetchall()
    conn.close()

    return render_template("index.html", songs=songs, liked_ids=[])


# ================= API (FUTURE REACT READY) =================
@app.route('/api/songs')
def api_songs():
    conn = get_db()
    songs = [dict(row) for row in conn.execute("SELECT * FROM songs")]
    conn.close()
    return {"songs": songs}