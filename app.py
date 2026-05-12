from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "corestudio-secret-2024"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///corestudio.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER_FILES"] = os.path.join("uploads", "files")
app.config["UPLOAD_FOLDER_IMAGES"] = os.path.join("uploads", "images")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

ADMIN_PASSWORD = "admin123"

db = SQLAlchemy(app)

# ---------- Model ----------
class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'mod' | 'plugin'
    description = db.Column(db.Text, default="")
    version = db.Column(db.String(50), default="1.0.0")
    mc_version = db.Column(db.String(50), default="")
    loader = db.Column(db.String(100), default="")
    author = db.Column(db.String(100), default="")
    downloads = db.Column(db.Integer, default=0)
    file_url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    os.makedirs(app.config["UPLOAD_FOLDER_FILES"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER_IMAGES"], exist_ok=True)

# ---------- Auth ----------
def is_admin():
    return session.get("admin") is True

# ---------- Routes ----------
@app.route("/")
def index():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    mods = [p for p in projects if p.type == "mod"]
    plugins = [p for p in projects if p.type == "plugin"]
    total_downloads = sum(p.downloads for p in projects)
    return render_template("index.html",
        projects=projects[:6],
        stats=dict(
            projects=len(projects),
            downloads=total_downloads,
            mods=len(mods),
            plugins=len(plugins)
        )
    )

@app.route("/mods")
def mods():
    items = Project.query.filter_by(type="mod").order_by(Project.created_at.desc()).all()
    return render_template("list.html", items=items, type="mod",
        title="Modlar", desc="Forge, Fabric, NeoForge va Quilt modlari")

@app.route("/plugins")
def plugins():
    items = Project.query.filter_by(type="plugin").order_by(Project.created_at.desc()).all()
    return render_template("list.html", items=items, type="plugin",
        title="Pluginlar", desc="Bukkit, Spigot va Paper pluginlari")

@app.route("/project/<id>")
def project_detail(id):
    p = Project.query.get_or_404(id)
    return render_template("project.html", p=p)

@app.route("/project/<id>/download")
def download(id):
    p = Project.query.get_or_404(id)
    p.downloads += 1
    db.session.commit()
    if p.file_url:
        return redirect(p.file_url)
    return redirect(url_for("project_detail", id=id))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    error = None
    if request.method == "POST" and not is_admin():
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        error = "Parol noto'g'ri"

    if is_admin():
        projects = Project.query.order_by(Project.created_at.desc()).all()
        return render_template("admin.html", projects=projects, authed=True)

    return render_template("admin.html", authed=False, error=error)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin"))

@app.route("/admin/add", methods=["POST"])
def admin_add():
    if not is_admin():
        return redirect(url_for("admin"))

    file_url = None
    image_url = None

    f = request.files.get("file")
    img = request.files.get("image")

    if f and f.filename:
        fname = f"{int(datetime.utcnow().timestamp())}-{secure_filename(f.filename)}"
        f.save(os.path.join(app.config["UPLOAD_FOLDER_FILES"], fname))
        file_url = url_for("serve_file", filename=fname, _external=True)

    if img and img.filename:
        iname = f"{int(datetime.utcnow().timestamp())}-{secure_filename(img.filename)}"
        img.save(os.path.join(app.config["UPLOAD_FOLDER_IMAGES"], iname))
        image_url = url_for("serve_image", filename=iname, _external=True)

    p = Project(
        name=request.form["name"],
        type=request.form["type"],
        description=request.form.get("description", ""),
        version=request.form.get("version", "1.0.0"),
        mc_version=request.form.get("mc_version", ""),
        loader=request.form.get("loader", ""),
        author=request.form.get("author", ""),
        file_url=file_url,
        image_url=image_url,
    )
    db.session.add(p)
    db.session.commit()
    return redirect(url_for("admin"))

@app.route("/admin/delete/<id>", methods=["POST"])
def admin_delete(id):
    if not is_admin():
        return redirect(url_for("admin"))
    p = Project.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for("admin"))

@app.route("/uploads/files/<filename>")
def serve_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER_FILES"], filename)

@app.route("/uploads/images/<filename>")
def serve_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER_IMAGES"], filename)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

