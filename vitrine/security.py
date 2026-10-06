"""Proteção dos formulários e controle de acesso."""
import hmac
import secrets
from functools import wraps
from flask import abort, g, redirect, request, session, url_for


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def init_app(app):
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def verify_csrf():
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            expected = session.get("csrf_token", "")
            provided = request.form.get("csrf_token", "")
            if not expected or not hmac.compare_digest(expected.encode("utf-8"), provided.encode("utf-8")):
                abort(400)
