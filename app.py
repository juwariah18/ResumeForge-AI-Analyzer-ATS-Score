from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, json
from datetime import datetime
from utils.resume_parser import extract_resume_photo, extract_resume_text
from utils.analyzer import analyze_resume, extract_resume_data
from utils.matcher import match_resume_to_job
from utils.pdf_generator import create_resume_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "resumeforge.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "development-secret-change-me")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf", "docx"}


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        source TEXT NOT NULL,
        data TEXT NOT NULL,
        template TEXT NOT NULL DEFAULT 'professional',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    conn.commit(); conn.close()


def login_required():
    if "user_id" not in session:
        flash("Please sign in first.", "warning")
        return False
    return True


def get_resume(resume_id):
    conn = db()
    row = conn.execute("SELECT * FROM resumes WHERE id=? AND user_id=?", (resume_id, session["user_id"])).fetchone()
    conn.close()
    return row


@app.context_processor
def inject_user():
    user = None
    if "user_id" in session:
        conn = db(); user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone(); conn.close()
    return {"current_user": user}


@app.route("/")
def home(): return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if not name or not email or len(password) < 6 or password != confirm:
            flash("Enter all fields. Passwords must match and contain at least 6 characters.", "danger")
            return render_template("auth.html", mode="signup")
        conn = db()
        try:
            cur = conn.execute("INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)", (name, email, generate_password_hash(password), datetime.utcnow().isoformat()))
            conn.commit(); session["user_id"] = cur.lastrowid
        except sqlite3.IntegrityError:
            flash("Email already registered. Please sign in.", "danger"); conn.close(); return render_template("auth.html", mode="signup")
        conn.close(); return redirect(url_for("choose_mode"))
    return render_template("auth.html", mode="signup")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower(); password = request.form.get("password", "")
        conn = db(); user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone(); conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]; return redirect(url_for("choose_mode"))
        flash("Invalid email or password.", "danger")
    return render_template("auth.html", mode="login")


@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("home"))


@app.route("/choose")
def choose_mode():
    if not login_required(): return redirect(url_for("login"))
    return render_template("choose.html")


def form_to_data(form):
    clean = {k: v for k, v in form.items()}
    for key in ["skills", "education", "experience", "projects", "certifications", "achievements", "languages", "soft_skills", "links"]:
        raw = form.get(key)
        if raw:
            try: clean[key] = json.loads(raw)
            except json.JSONDecodeError: clean[key] = raw
    return clean


def _photo_data_url(photo):
    import base64
    content = photo.read()
    if not content or not photo.mimetype.startswith("image/"):
        return ""
    return f"data:{photo.mimetype};base64,{base64.b64encode(content).decode('ascii')}"


@app.route("/create", methods=["GET", "POST"])
def create_resume():
    if not login_required(): return redirect(url_for("login"))
    if request.method == "POST":
        data = form_to_data(request.form)
        photo = request.files.get("photo")
        if photo and photo.filename:
            data["photo_data_url"] = _photo_data_url(photo)
        now = datetime.utcnow().isoformat()
        conn = db(); cur = conn.execute("INSERT INTO resumes(user_id,title,source,data,template,created_at,updated_at) VALUES(?,?,?,?,?,?,?)", (session["user_id"], data.get("full_name") or "My Resume", "scratch", json.dumps(data), data.get("template", "professional"), now, now)); conn.commit(); rid = cur.lastrowid; conn.close()
        return redirect(url_for("resume_result", resume_id=rid))
    return render_template("builder.html", data={}, resume_id=None)


@app.route("/upload", methods=["GET", "POST"])
def upload_resume():
    if not login_required(): return redirect(url_for("login"))
    if request.method == "POST":
        file = request.files.get("resume")
        if not file or not file.filename:
            flash("Choose a PDF or DOCX file.", "danger"); return redirect(url_for("upload_resume"))
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            flash("Only PDF and DOCX files are supported.", "danger"); return redirect(url_for("upload_resume"))
        filename = f"{session['user_id']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{secure_filename(file.filename)}"
        path = os.path.join(UPLOAD_DIR, filename); file.save(path)
        try: text = extract_resume_text(path, ext)
        except Exception as exc:
            flash(f"Could not read the file: {exc}", "danger"); return redirect(url_for("upload_resume"))
        data = extract_resume_data(text)
        data["photo_data_url"] = extract_resume_photo(path, ext)
        data["photo_choice"] = "yes" if data["photo_data_url"] else "no"
        now = datetime.utcnow().isoformat(); conn = db(); cur = conn.execute("INSERT INTO resumes(user_id,title,source,data,template,created_at,updated_at) VALUES(?,?,?,?,?,?,?)", (session["user_id"], "Uploaded Resume", "upload", json.dumps(data), "professional", now, now)); conn.commit(); rid = cur.lastrowid; conn.close()
        return redirect(url_for("edit_resume", resume_id=rid))
    return render_template("upload.html")


@app.route("/edit/<int:resume_id>", methods=["GET", "POST"])
def edit_resume(resume_id):
    if not login_required(): return redirect(url_for("login"))
    resume = get_resume(resume_id)
    if not resume: return "Resume not found", 404
    if request.method == "POST":
        data = form_to_data(request.form); data["raw_text"] = data.get("raw_text", "")
        existing_data = json.loads(resume["data"])
        data["photo_data_url"] = existing_data.get("photo_data_url", "")
        photo = request.files.get("photo")
        if photo and photo.filename:
            data["photo_data_url"] = _photo_data_url(photo)
        if data.get("photo_choice") == "no":
            data["photo_data_url"] = ""
        conn = db(); conn.execute("UPDATE resumes SET title=?,data=?,template=?,updated_at=? WHERE id=? AND user_id=?", (data.get("full_name") or "My Resume", json.dumps(data), data.get("template", "professional"), datetime.utcnow().isoformat(), resume_id, session["user_id"])); conn.commit(); conn.close()
        return redirect(url_for("resume_result", resume_id=resume_id))
    return render_template("builder.html", data=json.loads(resume["data"]), resume_id=resume_id)


@app.route("/result/<int:resume_id>")
def resume_result(resume_id):
    if not login_required(): return redirect(url_for("login"))
    resume = get_resume(resume_id)
    if not resume: return "Resume not found", 404
    data = json.loads(resume["data"]); text = data.get("raw_text") or json.dumps(data); data["analysis"] = analyze_resume(text)
    return render_template("result.html", resume=data, resume_id=resume_id)


@app.route("/match/<int:resume_id>", methods=["POST"])
def match_job(resume_id):
    if not login_required(): return redirect(url_for("login"))
    resume = get_resume(resume_id)
    if not resume: return "Resume not found", 404
    job = request.form.get("job_description", "").strip(); data = json.loads(resume["data"]); text = data.get("raw_text") or json.dumps(data)
    result = match_resume_to_job(text, job)
    return render_template("match.html", result=result, resume_id=resume_id)

@app.route("/home-job-match", methods=["POST"])
def home_job_match():
    file = request.files.get("resume")
    job = (request.form.get("job_description") or "").strip()

    if not file or not file.filename:
        flash("Please choose a resume file (PDF or DOCX).", "danger")
        return redirect(url_for("home") + "#jobMatchHome")

    if not job:
        flash("Please paste a job description.", "danger")
        return redirect(url_for("home") + "#jobMatchHome")

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        flash("Only PDF and DOCX files are supported.", "danger")
        return redirect(url_for("home") + "#jobMatchHome")

    path = os.path.join(
        UPLOAD_DIR,
        f"match_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{filename}"
    )
    file.save(path)

    try:
        resume_text = extract_resume_text(path, ext)
    except Exception as exc:
        flash(f"Could not read the file: {exc}", "danger")
        return redirect(url_for("home") + "#jobMatchHome")

    result = match_resume_to_job(resume_text, job)
    return render_template("match.html", result=result, resume_id=None)

@app.route("/download/<int:resume_id>")
def download_resume(resume_id):
    if not login_required(): return redirect(url_for("login"))
    resume = get_resume(resume_id)
    if not resume: return "Resume not found", 404
    data = json.loads(resume["data"]); output = os.path.join(UPLOAD_DIR, f"resume_{resume_id}.pdf"); create_resume_pdf(data, output)
    return send_file(output, as_attachment=True, download_name="ResumeForge_Resume.pdf", mimetype="application/pdf")


@app.route("/my-resumes")
def my_resumes():
    if not login_required(): return redirect(url_for("login"))
    conn = db(); resumes = conn.execute("SELECT * FROM resumes WHERE user_id=? ORDER BY updated_at DESC", (session["user_id"],)).fetchall(); conn.close()
    return render_template("my_resumes.html", resumes=resumes)


@app.errorhandler(413)
def too_large(_): return "File too large. Maximum size is 8 MB.", 413


init_db()

if __name__ == "__main__":
    app.run(debug=True)


