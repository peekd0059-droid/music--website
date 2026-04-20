@app.route("/like", methods=["POST"])
def like_song():
    if "user" not in session:
        return "Login required"

    try:
        data = request.get_json()

        name = data.get("name")
        file = data.get("file")
        image = data.get("image")

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "INSERT INTO liked_songs (user, name, file, image) VALUES (?, ?, ?, ?)",
            (session["user"], name, file, image)
        )

        conn.commit()
        conn.close()

        return jsonify({"status": "ok"})

    except Exception as e:
        print("ERROR:", e)
        return "Error"


@app.route("/liked")
def liked():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM liked_songs WHERE user=?", (session["user"],))
    data = c.fetchall()

    songs = []
    for row in data:
        songs.append({
            "name": row["name"],
            "file": row["file"],
            "image": row["image"]
        })

    conn.close()

    return render_template("liked.html", songs=songs)
