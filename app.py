import csv
import hmac
import io
import os
import re
import secrets
import sqlite3
import uuid
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_wtf.csrf import CSRFProtect, CSRFError
from markupsafe import Markup, escape
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Without SECRET_KEY set, fall back to a random key: admin sessions reset on
# every restart, but nobody can forge one from a key that's published in the repo.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
if "SECRET_KEY" not in os.environ:
    app.logger.warning("SECRET_KEY is not set; using a random key for this process.")

ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    WTF_CSRF_TIME_LIMIT=None,  # tokens last as long as the session
)
csrf = CSRFProtect(app)

DB_PATH = os.path.join(app.root_path, "database.db")
SCHEMA_PATH = os.path.join(app.root_path, "schema.sql")

# -------- Upload Config --------
UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
GALLERY_FOLDER = os.path.join(app.static_folder, "gallery_uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GALLERY_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
POST_KINDS = ("Journal", "Note", "Essay")
GALLERY_TAGS = ("nature", "portraits", "candids", "experimental")

# Web-sized copies of photos live under static/web/, mirroring the original path.
WEB_IMAGE_DIR = "web"
WEB_IMAGE_MAX_SIZE = 2000  # longest edge, in pixels


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file, folder):
    """Save an uploaded file under a unique name and return its static-relative path."""
    unique_name = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file.save(os.path.join(app.static_folder, folder, unique_name))
    rel_path = f"{folder}/{unique_name}"
    make_web_image(rel_path)
    return rel_path
# --------------------------------

# -------- Web-sized images --------
def web_image_path(rel_path):
    """static-relative path of the web-sized copy, e.g. web/photos/hero/IMG_1.webp"""
    return f"{WEB_IMAGE_DIR}/{os.path.splitext(rel_path)[0]}.webp"


def make_web_image(rel_path):
    """Write a resized WebP copy of a static image. EXIF (including GPS) is dropped."""
    src = os.path.join(app.static_folder, rel_path)
    dest = os.path.join(app.static_folder, web_image_path(rel_path))
    if os.path.exists(dest) or not os.path.exists(src):
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img)  # phone photos store rotation in EXIF
        img.thumbnail((WEB_IMAGE_MAX_SIZE, WEB_IMAGE_MAX_SIZE))
        img.save(dest, "WEBP", quality=82, method=6)


@app.template_filter("web_url")
def web_url(path):
    """URL for a photo, preferring its web-sized copy when one exists.

    Accepts a static-relative path ("photos/x.jpeg") or a URL ("/static/uploads/x.jpeg").
    """
    rel_path = path.removeprefix("/static/")
    web_path = web_image_path(rel_path)
    if os.path.exists(os.path.join(app.static_folder, web_path)):
        return url_for("static", filename=web_path)
    return url_for("static", filename=rel_path)


@app.template_filter("highlight")
def highlight(text, query):
    """Escape text and wrap case-insensitive matches of query in <mark>."""
    escaped = str(escape(text))
    if not query:
        return Markup(escaped)
    pattern = re.compile(re.escape(str(escape(query))), re.IGNORECASE)
    return Markup(pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", escaped))


def delete_static_file(url):
    """Remove an uploaded image and its web-sized copy. Missing files are ignored."""
    rel_path = url.removeprefix("/static/")
    for path in (rel_path, web_image_path(rel_path)):
        try:
            os.remove(os.path.join(app.static_folder, path))
        except OSError:
            pass


@app.cli.command("make-web-images")
def make_web_images_command():
    """Generate web-sized copies of every photo the site uses."""
    with get_db() as db:
        paths = [r[0] for r in db.execute("SELECT filename FROM gallery")]
        paths += [r[0] for r in db.execute("SELECT image_url FROM posts WHERE image_url IS NOT NULL")]
    template_dir = os.path.join(app.root_path, "templates")
    for name in os.listdir(template_dir):
        with open(os.path.join(template_dir, name), encoding="utf-8") as f:
            paths += re.findall(r"photos/[^'\")\s]+\.(?:jpe?g|png|webp)", f.read())

    for path in sorted(set(p.removeprefix("/static/") for p in paths)):
        make_web_image(path)
    print(f"Checked {len(set(paths))} images.")
# --------------------------------


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with open(SCHEMA_PATH, encoding="utf-8") as f, get_db() as db:
        db.executescript(f.read())


# ensure db tables exist
init_db()


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_globals():
    return dict(site_title="Alejandro Ines")


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash("Your session expired. Please try again.", "warning")
    return redirect(request.referrer or url_for("index"))


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
        posts = db.execute(
            "SELECT id, title, kind, body, created, image_url FROM posts ORDER BY created DESC"
        ).fetchall()
    return render_template("blog.html", posts=posts)


# ──────────────── Post Detail ────────────────
@app.route("/post/<int:post_id>")
def post_detail(post_id):
    with get_db() as db:
        post = db.execute(
            "SELECT id, title, kind, body, created, image_url FROM posts WHERE id = ?",
            (post_id,)
        ).fetchone()
    if not post:
        flash("Post not found.", "warning")
        return redirect(url_for("blog"))
    return render_template("post_detail.html", post=post)


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = (request.form.get("email") or "").strip().lower()
    if "@" not in email:
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
        # Escape LIKE wildcards so a search for "100%" matches literally
        pattern = "%" + re.sub(r"([\\%_])", r"\\\1", query) + "%"
        with get_db() as db:
            post_results = db.execute(
                """SELECT id, title, kind, body, created, image_url FROM posts
                   WHERE lower(title) LIKE ? ESCAPE '\\' OR lower(body) LIKE ? ESCAPE '\\'
                   ORDER BY created DESC""",
                (pattern, pattern)
            ).fetchall()
            photo_results = db.execute(
                """SELECT id, filename, tag, created FROM gallery
                   WHERE tag LIKE ? ESCAPE '\\' OR lower(filename) LIKE ? ESCAPE '\\'
                   ORDER BY created DESC""",
                (pattern, pattern)
            ).fetchall()

    return render_template("search.html", query=query, post_results=post_results, photo_results=photo_results)


# ──────────────── Admin ────────────────
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password") or ""
        if hmac.compare_digest(password.encode(), ADMIN_PASSWORD.encode()):
            session.clear()
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
@admin_required
def admin_panel():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        kind = (request.form.get("kind") or "Journal").strip()
        body = (request.form.get("body") or "").strip()

        if not title or not body:
            flash("Title and body required.", "warning")
        elif kind not in POST_KINDS:
            flash("Invalid post kind.", "warning")
        else:
            image_url = None
            file = request.files.get("image")
            if file and file.filename and allowed_file(file.filename):
                image_url = "/static/" + save_upload(file, "uploads")
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
@admin_required
def admin_delete(post_id):
    with get_db() as db:
        row = db.execute("SELECT image_url FROM posts WHERE id = ?", (post_id,)).fetchone()
        if row and row["image_url"]:
            delete_static_file(row["image_url"])
        db.execute("DELETE FROM posts WHERE id = ?", (post_id,))

    flash("Post and image deleted.", "info")
    return redirect(url_for("admin_panel"))


@app.route("/admin/export-subscribers")
@admin_required
def export_subscribers():
    with get_db() as db:
        subs = db.execute("SELECT email, created FROM subscribers ORDER BY created DESC").fetchall()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["email", "created"])
    for s in subs:
        cw.writerow([s["email"], s["created"]])
    output = io.BytesIO(si.getvalue().encode("utf-8"))
    return send_file(output, mimetype="text/csv", as_attachment=True, download_name="subscribers.csv")


# ──────────────── Gallery Admin Routes ────────────────
@app.route("/admin/gallery/upload", methods=["POST"])
@admin_required
def gallery_upload():
    files = request.files.getlist("images")
    tag = request.form.get("tag")

    if not files or tag not in GALLERY_TAGS:
        flash("Please choose files and a tag.", "warning")
        return redirect(url_for("admin_panel"))

    with get_db() as db:
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                rel_path = "/static/" + save_upload(file, "gallery_uploads")
                db.execute("INSERT INTO gallery (filename, tag) VALUES (?, ?)", (rel_path, tag))

    flash("Photos uploaded.", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/gallery/edit/<int:photo_id>", methods=["POST"])
@admin_required
def gallery_edit(photo_id):
    new_tag = request.form.get("tag")
    if new_tag not in GALLERY_TAGS:
        flash("Invalid tag.", "warning")
    else:
        with get_db() as db:
            db.execute("UPDATE gallery SET tag = ? WHERE id = ?", (new_tag, photo_id))
        flash("Photo updated.", "success")

    return redirect(url_for("admin_panel"))


@app.route("/admin/gallery/delete/<int:photo_id>", methods=["POST"])
@admin_required
def gallery_delete(photo_id):
    with get_db() as db:
        row = db.execute("SELECT filename FROM gallery WHERE id = ?", (photo_id,)).fetchone()
        if row:
            delete_static_file(row["filename"])
        db.execute("DELETE FROM gallery WHERE id = ?", (photo_id,))

    flash("Photo deleted.", "info")
    return redirect(url_for("admin_panel"))


if __name__ == "__main__":
    # CITE AI usage (CS50 requirement): scaffolding generated with AI assistants
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", port=5000)
