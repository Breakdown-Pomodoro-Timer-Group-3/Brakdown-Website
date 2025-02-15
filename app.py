from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this for security

# Initialize database
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Homepage Route
@app.route("/")
def home():
    return render_template("home.html")


# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[0]):  
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("timer"))
        else:
            flash("Invalid username or password!", "error")

    return render_template("login.html")


# Registration Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists. Try a different one.", "error")

        conn.close()

    return render_template("register.html")


# Timer Page (Protected Route)
@app.route("/timer")
def timer():
    if "user" not in session:  # Redirect if not logged in
        flash("You must be logged in to access the timer.", "error")
        return redirect(url_for("login"))

    return render_template("index.html", username=session["user"])


# Logout Route
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# Run the app
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
