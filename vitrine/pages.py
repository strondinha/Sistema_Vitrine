from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)


@bp.get("/sobre")
def about():
    return render_template("about.html")
