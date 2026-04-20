from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


# ===== DATABASE =====
def get_db():
    return sqlite3.connect("songs.db")


# ===== HOME =====
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return "Home working"


# ===== LOGIN =====
@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            conn = get_db()
            c = conn.cursor()

            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()

            conn.close()

            if user:
                session["user"] = username
                return redirect("/")
            else:
                return "Invalid Login"

        return render_template("login.html")

    except Exception as e:
        print("LOGIN ERROR:", e)
        return "Login Error"


# ===== SIGNUP =====
@app.route("/signup", methods=["GET", "POST"])
def signup():
    try:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            conn = get_db()
            c = conn.cursor()

            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()

            return redirect("/login")

        return render_template("signup.html")

    except Exception as e:
        print("SIGNUP ERROR:", e)
        return "Signup Error"


# ===== LOGOUT =====
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)
