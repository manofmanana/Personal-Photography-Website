from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import sqlite3, os, csv, io, uuid
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

# -------- Upload Config --------
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
GALLERY_FOLDER = os.path.join(app.root_path, "static", "gallery_uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GALLERY_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["GALLERY_FOLDER"] = GALLERY_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
# --------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    schema = """
    PRAGMA foreign_keys=ON;

    CREATE TABLE IF NOT EXISTS posts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      kind TEXT NOT NULL DEFAULT "Journal",
      body TEXT NOT NULL,
      image_url TEXT,
      created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS subscribers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT NOT NULL UNIQUE,
      created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL,
      message TEXT NOT NULL,
      created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS gallery (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      filename TEXT NOT NULL,
      tag TEXT NOT NULL CHECK (tag IN ('nature','portraits','candids','experimental')),
      created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_db() as db:
        db.executescript(schema)

# ensure db tables exist
init_db()

@app.context_processor
def inject_globals():
    return dict(site_title="Alejandro Ines")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gallery")
def gallery():
    with get_db() as db:
        photos = db.execute(
            "SELECT id, filename, tag, created FROM gallery ORDER BY created DESC"
        ).fetchall()
    return render_template("gallery.html", photos=photos)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/blog")
def blog():
    with get_db() as db:
        rows = db.execute(
            "SELECT id, title, kind, body, created, image_url FROM posts ORDER BY created DESC"
        ).fetchall()
    posts = []
    for r in rows:
        posts.append({
            "id": r["id"],
            "title": r["title"],
            "kind": r["kind"],
            "body": r["body"] or "",
            "created": r["created"],
            "image_url": r["image_url"]
        })
    return render_template("blog.html", posts=posts)

# ──────────────── Post Detail ────────────────
@app.route("/post/<int:post_id>")
def post_detail(post_id):
    with get_db() as db:
        r = db.execute(
            "SELECT id, title, kind, body, created, image_url FROM posts WHERE id = ?",
            (post_id,)
        ).fetchone()
    if not r:
        flash("Post not found.", "warning")
        return redirect(url_for("blog"))
    post = {
        "id": r["id"],
        "title": r["title"],
        "kind": r["kind"],
        "body": r["body"] or "",
        "created": r["created"],
        "image_url": r["image_url"]
    }
    return render_template("post_detail.html", post=post)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = (request.form.get("email") or "").strip().lower()
    if not email:
        flash("Enter a valid email.", "warning")
        return redirect(url_for("index"))
    try:
        with get_db() as db:
            db.execute("INSERT INTO subscribers (email) VALUES (?)", (email,))
        flash("You are on the list. The next photo will find you.", "success")
    except sqlite3.IntegrityError:
        flash("That email is already subscribed.", "info")
    return redirect(url_for("index"))

# ──────────────── Search ────────────────
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip().lower()
    post_results = []
    photo_results = []

    if query:
        # --- Search blog posts ---
        with get_db() as db:
            rows = db.execute(
                "SELECT id, title, kind, body, created, image_url FROM posts ORDER BY created DESC"
            ).fetchall()
        for r in rows:
            if query in (r["title"] or "").lower() or query in (r["body"] or "").lower():
                post_results.append({
                    "id": r["id"],
                    "title": r["title"],
                    "kind": r["kind"],
                    "body": r["body"] or "",
                    "created": r["created"],
                    "image_url": r["image_url"]
                })

        # --- Search gallery photos (by tag or filename) ---
        with get_db() as db:
            photos = db.execute(
                "SELECT id, filename, tag, created FROM gallery ORDER BY created DESC"
            ).fetchall()
        for p in photos:
            if query in (p["tag"] or "").lower() or query in (p["filename"] or "").lower():
                photo_results.append({
                    "id": p["id"],
                    "filename": p["filename"],
                    "tag": p["tag"],
                    "created": p["created"]
                })

    return render_template("search.html", query=query, post_results=post_results, photo_results=photo_results)

# ──────────────── Admin ────────────────
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin_panel"))
        flash("Incorrect password.", "danger")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        kind = (request.form.get("kind") or "Journal").strip()
        body = (request.form.get("body") or "").strip()

        image_url = None
        file = request.files.get("image")
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
            file.save(filepath)
            image_url = f"/static/uploads/{unique_name}"

        if not title or not body:
            flash("Title and body required.", "warning")
        else:
            with get_db() as db:
                db.execute(
                    "INSERT INTO posts (title, kind, body, image_url) VALUES (?, ?, ?, ?)",
                    (title, kind, body, image_url)
                )
            flash("Post published.", "success")
        return redirect(url_for("admin_panel"))

    with get_db() as db:
        posts = db.execute(
            "SELECT id, title, kind, created, image_url FROM posts ORDER BY created DESC"
        ).fetchall()
        subs = db.execute("SELECT email, created FROM subscribers ORDER BY created DESC").fetchall()
        gallery = db.execute("SELECT id, filename, tag, created FROM gallery ORDER BY created DESC").fetchall()
    return render_template("admin.html", posts=posts, subs=subs, gallery=gallery)

@app.route("/admin/delete/<int:post_id>", methods=["POST"])
def admin_delete(post_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    with get_db() as db:
        row = db.execute("SELECT image_url FROM posts WHERE id = ?", (post_id,)).fetchone()
        if row and row["image_url"]:
            image_path = row["image_url"].lstrip("/")
            fs_path = os.path.join(app.root_path, image_path)
            if os.path.exists(fs_path):
                try:
                    os.remove(fs_path)
                except OSError:
                    pass
        db.execute("DELETE FROM posts WHERE id = ?", (post_id,))

    flash("Post and image deleted.", "info")
    return redirect(url_for("admin_panel"))

@app.route("/admin/export-subscribers")
def export_subscribers():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    with get_db() as db:
        subs = db.execute("SELECT email, created FROM subscribers ORDER BY created DESC").fetchall()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["email", "created"])
    for s in subs:
        cw.writerow([s["email"], s["created"]])
    output = io.BytesIO()
    output.write(si.getvalue().encode("utf-8"))
    output.seek(0)
    return send_file(output, mimetype="text/csv", as_attachment=True, download_name="subscribers.csv")

# ──────────────── Gallery Admin Routes ────────────────
@app.route("/admin/gallery/upload", methods=["POST"])
def gallery_upload():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    files = request.files.getlist("images")
    tag = request.form.get("tag")

    if not files or not tag:
        flash("Please choose files and a tag.", "warning")
        return redirect(url_for("admin_panel"))

    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config["GALLERY_FOLDER"], unique_name)
            file.save(filepath)

            rel_path = f"/static/gallery_uploads/{unique_name}"
            with get_db() as db:
                db.execute("INSERT INTO gallery (filename, tag) VALUES (?, ?)", (rel_path, tag))

    flash("Photos uploaded.", "success")
    return redirect(url_for("admin_panel"))

@app.route("/admin/gallery/edit/<int:photo_id>", methods=["POST"])
def gallery_edit(photo_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    new_tag = request.form.get("tag")
    if new_tag not in ("nature", "portraits", "candids", "experimental"):
        flash("Invalid tag.", "warning")
    else:
        with get_db() as db:
            db.execute("UPDATE gallery SET tag = ? WHERE id = ?", (new_tag, photo_id))
        flash("Photo updated.", "success")

    return redirect(url_for("admin_panel"))

@app.route("/admin/gallery/delete/<int:photo_id>", methods=["POST"])
def gallery_delete(photo_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    with get_db() as db:
        row = db.execute("SELECT filename FROM gallery WHERE id = ?", (photo_id,)).fetchone()
        if row:
            image_path = row["filename"].lstrip("/")
            fs_path = os.path.join(app.root_path, image_path)
            if os.path.exists(fs_path):
                try:
                    os.remove(fs_path)
                except OSError:
                    pass
        db.execute("DELETE FROM gallery WHERE id = ?", (photo_id,))

    flash("Photo deleted.", "info")
    return redirect(url_for("admin_panel"))

if __name__ == "__main__":
    # CITE AI usage (CS50 requirement): scaffolding generated with AI assistants
    app.run(debug=True, host="0.0.0.0", port=5000)
