import os
import time
from urllib.parse import quote_plus

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- PART 1: Which database? ---
# On AWS, ECS gives us DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
# (the password comes from Secrets Manager via ValueFrom).
# On your laptop these are not set, so we use a local file (SQLite).
db_host = os.environ.get("DB_HOST")
if db_host:
    user = os.environ.get("DB_USER", "postgres")
    password = quote_plus(os.environ.get("DB_PASSWORD", ""))
    name = os.environ.get("DB_NAME", "postgres")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
               f"postgresql+psycopg2://{user}:{password}@{db_host}:5432/{name}"
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"

db = SQLAlchemy(app)


# --- PART 2: The "tasks" table ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)


with app.app_context():
    db.create_all()  # creates the table if it doesn't exist yet


# --- PART 3: The pages ---
@app.route("/")
def home():
    tasks = Task.query.order_by(Task.done, Task.id.desc()).all()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        db.session.add(Task(title=title))
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/done/<int:task_id>", methods=["POST"])
def toggle_done(task_id):
    task = db.get_or_404(Task, task_id)
    task.done = not task.done
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    task = db.get_or_404(Task, task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template("about.html", hostname=os.environ.get("HOSTNAME", "laptop"))


# --- PART 4: For AWS ---
@app.route("/health")
def health():
    return "ok", 200  # the ALB knocks here to check the container is alive


@app.route("/burn")
def burn():
    end = time.time() + 30  # keep the CPU busy for 30 seconds
    while time.time() < end:
        pass
    return "Burned CPU for 30 seconds"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)