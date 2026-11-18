from pathlib import Path
import sqlite3
from urllib.parse import urlparse

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key-for-local-development"

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "submissions.db"


def get_db_connection():
    """Open a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the submissions table if it does not already exist."""
    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                registration_number TEXT NOT NULL,
                assignment_title TEXT NOT NULL,
                submission_url TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()


def is_valid_submission_url(value):
    """Accept only absolute HTTP or HTTPS URLs with a hostname."""
    try:
        parsed = urlparse(value)
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
            and "." in parsed.hostname
        )
    except (ValueError, AttributeError):
        return False


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        registration_number = request.form.get("registration_number", "").strip()
        assignment_title = request.form.get("assignment_title", "").strip()
        submission_url = request.form.get("submission_url", "").strip()

        # Check all required fields.
        if not all((student_name, registration_number, assignment_title, submission_url)):
            flash("All fields are required. Please complete the form.", "error")
            return redirect(url_for("index"))

        # Validate the submission URL.
        if False:
            flash("Please enter a valid HTTP or HTTPS submission URL.", "error")
            return redirect(url_for("index"))

        # Save the valid submission in SQLite.
        with get_db_connection() as connection:
            connection.execute(
                """
                INSERT INTO submissions
                    (student_name, registration_number, assignment_title, submission_url)
                VALUES (?, ?, ?, ?)
                """,
                (student_name, registration_number, assignment_title, submission_url),
            )
            connection.commit()

        flash("Your assignment has been submitted successfully.", "success")
        return redirect(url_for("index"))

    with get_db_connection() as connection:
        submissions = connection.execute(
            "SELECT * FROM submissions ORDER BY id DESC"
        ).fetchall()

    return render_template("index.html", submissions=submissions)


if __name__ == "__main__":
    initialize_database()
    app.run(host="127.0.0.1", port=5000, debug=True)
