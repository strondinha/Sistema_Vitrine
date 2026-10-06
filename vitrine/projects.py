"""Catálogo público e operações dos responsáveis pelos projetos."""
import math
from datetime import date
from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, send_from_directory, url_for
from .db import get_db, fold_text
from .security import login_required
from .uploads import MAX_IMAGES, remove_files, save_images
from .validation import AREAS, CATEGORIES, COURSES, project_data

bp = Blueprint("projects", __name__)
PROJECT_SELECT = """SELECT p.*, u.name AS owner_name,
    (SELECT filename FROM project_images WHERE project_id = p.id ORDER BY id LIMIT 1) AS cover
    FROM projects p JOIN users u ON u.id = p.user_id"""


def get_project(project_id, owner_only=False):
    project = get_db().execute(PROJECT_SELECT + " WHERE p.id = ?", (project_id,)).fetchone()
    if project is None:
        abort(404)
    is_owner = g.user is not None and g.user["id"] == project["user_id"]
    if owner_only and not is_owner:
        abort(403)
    if project["status"] != "published" and not is_owner:
        abort(404)
    return project


def filter_options():
    connection = get_db()
    return {field: [row[0] for row in connection.execute(
        f"SELECT DISTINCT {field} FROM projects WHERE status = 'published' ORDER BY {field}" + (" DESC" if field == "year" else "")
    )] for field in ("course", "area", "year")}


@bp.get("/")
def index():
    filters = {key: request.args.get(key, "").strip() for key in ("q", "course", "area", "year", "category")}
    clauses = ["p.status = 'published'"]
    params = []
    if filters["q"]:
        # Escape dos curingas para que a pesquisa seja literal.
        term = fold_text(filters["q"][:200]).replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        clauses.append("(fold_text(p.title) LIKE ? ESCAPE '\\' OR fold_text(p.summary) LIKE ? ESCAPE '\\' OR fold_text(p.team) LIKE ? ESCAPE '\\')")
        params.extend([f"%{term}%"] * 3)
    for field in ("course", "area", "year", "category"):
        if filters[field]:
            clauses.append(f"p.{field} = ?")
            params.append(filters[field])
    where = " WHERE " + " AND ".join(clauses)
    total = get_db().execute("SELECT COUNT(*) FROM projects p" + where, params).fetchone()[0]
    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1
    pages = max(1, math.ceil(total / 9))
    page = min(page, pages)
    projects = get_db().execute(PROJECT_SELECT + where + " ORDER BY p.created_at DESC, p.id DESC LIMIT 9 OFFSET ?", params + [(page - 1) * 9]).fetchall()
    stats = get_db().execute("SELECT COUNT(*) AS projects, COUNT(DISTINCT course) AS courses, COUNT(DISTINCT area) AS areas FROM projects WHERE status = 'published'").fetchone()
    return render_template("projects/index.html", projects=projects, filters=filters, options=filter_options(),
                           categories=CATEGORIES, stats=stats, total=total, page=page, pages=pages)


@bp.get("/projetos/<int:project_id>")
def detail(project_id):
    project = get_project(project_id)
    images = get_db().execute("SELECT * FROM project_images WHERE project_id = ? ORDER BY id", (project_id,)).fetchall()
    return render_template("projects/detail.html", project=project, images=images)


@bp.get("/meus-projetos")
@login_required
def dashboard():
    projects = get_db().execute(PROJECT_SELECT + " WHERE p.user_id = ? ORDER BY p.updated_at DESC, p.id DESC", (g.user["id"],)).fetchall()
    return render_template("projects/dashboard.html", projects=projects,
                           published=sum(p["status"] == "published" for p in projects))


def project_form(project=None):
    project_id = project["id"] if project else None
    connection = get_db()
    images = connection.execute("SELECT * FROM project_images WHERE project_id = ? ORDER BY id", (project_id,)).fetchall() if project else []
    data = dict(project) if project else {"year": date.today().year, "category": "Ensino", "status": "draft", "team": g.user["name"], "contact_email": g.user["email"]}
    errors = []
    if request.method == "POST":
        data, errors = project_data(request.form)
        uploads = [image for image in request.files.getlist("images") if image.filename]
        existing_ids = {str(image["id"]) for image in images}
        removed_ids = set(request.form.getlist("remove_images"))
        if not removed_ids.issubset(existing_ids):
            abort(400)
        removed = [image for image in images if str(image["id"]) in removed_ids]
        if len(images) - len(removed) + len(uploads) > MAX_IMAGES:
            errors.append(f"Cada projeto pode ter no máximo {MAX_IMAGES} imagens.")
        saved = []
        if not errors:
            try:
                saved = save_images(uploads)
            except ValueError as error:
                errors.append(str(error))
        if not errors:
            try:
                fields = list(data)
                if project:
                    assignments = ", ".join(f"{field} = ?" for field in fields)
                    connection.execute(f"UPDATE projects SET {assignments}, updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') WHERE id = ?", list(data.values()) + [project_id])
                else:
                    columns = ", ".join(["user_id"] + fields)
                    placeholders = ", ".join(["?"] * (len(fields) + 1))
                    project_id = connection.execute(f"INSERT INTO projects ({columns}) VALUES ({placeholders})", [g.user["id"]] + list(data.values())).lastrowid
                for image in removed:
                    connection.execute("DELETE FROM project_images WHERE id = ? AND project_id = ?", (image["id"], project_id))
                for filename, original_name in saved:
                    connection.execute("INSERT INTO project_images (project_id, filename, original_name) VALUES (?, ?, ?)", (project_id, filename, original_name))
                connection.commit()
            except Exception:
                connection.rollback()
                remove_files([image[0] for image in saved])
                raise
            remove_files([image["filename"] for image in removed])
            flash("Projeto publicado! Ele já aparece na vitrine." if data["status"] == "published" else "Rascunho salvo. Apenas você pode visualizá-lo.", "success")
            return redirect(url_for("projects.detail", project_id=project_id))
    return render_template("projects/form.html", form=data, project=project, images=images,
                           errors=errors, courses=COURSES, areas=AREAS, categories=CATEGORIES), (400 if errors else 200)


@bp.route("/projetos/novo", methods=["GET", "POST"])
@login_required
def create():
    return project_form()


@bp.route("/projetos/<int:project_id>/editar", methods=["GET", "POST"])
@login_required
def edit(project_id):
    return project_form(get_project(project_id, owner_only=True))


@bp.post("/projetos/<int:project_id>/excluir")
@login_required
def delete(project_id):
    get_project(project_id, owner_only=True)
    connection = get_db()
    images = connection.execute("SELECT filename FROM project_images WHERE project_id = ?", (project_id,)).fetchall()
    connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    connection.commit()
    remove_files([image["filename"] for image in images])
    flash("Projeto excluído.", "success")
    return redirect(url_for("projects.dashboard"))


@bp.get("/imagens/<filename>")
def image(filename):
    record = get_db().execute("SELECT project_id FROM project_images WHERE filename = ?", (filename,)).fetchone()
    if record is None:
        abort(404)
    get_project(record["project_id"])
    response = send_from_directory(current_app.config["UPLOAD_FOLDER"], filename, max_age=0)
    response.headers["Cache-Control"] = "no-store"
    return response
