from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Database setup
def init_db():
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    location TEXT,
                    issue TEXT,
                    severity TEXT,
                    comments TEXT,
                    photo TEXT
                )""")
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    authority_emails = {
        "PWD": "pwd@gov.com",
      "LDA": "lda@gov.com",
      "Nagar Nigam": "nagarnigam@gov.com",
      "Municipality": "municipality@gov.com",
      "Urban development": "urbandev@gov.com"
    }

    name = request.form["name"]
    location = request.form["location"]
    issue = request.form["issue"]
    severity = request.form["severity"]
    comments = request.form["comments"]
    authority = request.form["authority"]
    authority_email = authority_emails.get(authority, "")

    photo_file = request.files["photo"]
    photo_path = None
    if photo_file and photo_file.filename != "":
        photo_path = os.path.join(app.config["UPLOAD_FOLDER"], photo_file.filename)
        photo_file.save(photo_path)

    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute("INSERT INTO feedback (name, location, issue, severity, comments, photo) VALUES (?,?,?,?,?,?)",
              (name, location, issue, severity, comments, photo_path))
    conn.commit()
    conn.close()

    # Pass authority and email to thank you page
    return redirect(url_for("thankyou", authority=authority, email=authority_email))

@app.route("/thankyou")
def thankyou():
    authority = request.args.get("authority", "PWD")
    email = request.args.get("email", "pwd@example.com")
    return render_template("thankyou.html", authority=authority, email=email)

@app.route("/report")
def reports():
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute("SELECT * FROM feedback")
    rows = c.fetchall()
    conn.close()
    return render_template("report.html", rows=rows)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)