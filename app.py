from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "helpdesk.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db_connection()

    tickets = conn.execute(
        "SELECT * FROM tickets ORDER BY id DESC"
    ).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) FROM tickets"
    ).fetchone()[0]

    open_tickets = conn.execute(
        "SELECT COUNT(*) FROM tickets WHERE status = 'Open'"
    ).fetchone()[0]

    progress_tickets = conn.execute(
        "SELECT COUNT(*) FROM tickets WHERE status = 'In Progress'"
    ).fetchone()[0]

    resolved_tickets = conn.execute(
        "SELECT COUNT(*) FROM tickets WHERE status = 'Resolved'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        tickets=tickets,
        total=total,
        open_tickets=open_tickets,
        progress_tickets=progress_tickets,
        resolved_tickets=resolved_tickets
    )


@app.route("/create", methods=["GET", "POST"])
def create_ticket():
    if request.method == "POST":
        employee_name = request.form.get("employee_name", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "")
        priority = request.form.get("priority", "")

        allowed_categories = [
            "Hardware", "Software", "Network", "Account Access"
        ]

        allowed_priorities = ["Low", "Medium", "High"]

        if (
            not employee_name
            or not title
            or not description
            or category not in allowed_categories
            or priority not in allowed_priorities
        ):
            return "Invalid input. Please check your details.", 400

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO tickets (
                employee_name, title, description,
                category, priority, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            employee_name,
            title,
            description,
            category,
            priority,
            "Open",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("create_ticket.html")


@app.route("/ticket/<int:ticket_id>")
def ticket_details(ticket_id):
    conn = get_db_connection()

    ticket = conn.execute(
        "SELECT * FROM tickets WHERE id = ?",
        (ticket_id,)
    ).fetchone()

    conn.close()

    if ticket is None:
        return "Ticket not found", 404

    return render_template("ticket_details.html", ticket=ticket)


@app.route("/update/<int:ticket_id>", methods=["POST"])
def update_ticket(ticket_id):
    status = request.form.get("status", "")

    if status not in ["Open", "In Progress", "Resolved"]:
        return "Invalid status", 400

    conn = get_db_connection()

    conn.execute(
        "UPDATE tickets SET status = ? WHERE id = ?",
        (status, ticket_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("ticket_details", ticket_id=ticket_id))


if __name__ == "__main__":
    initialize_database()
    print("Starting IT Help Desk System...")
    app.run(debug=True)