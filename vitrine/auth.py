"""Cadastro, login e encerramento de sessão."""
import sqlite3
import time
from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db
from .validation import valid_email

bp = Blueprint("auth", __name__, url_prefix="/conta")


@bp.before_app_request
def load_user():
    user_id = session.get("user_id")
    g.user = get_db().execute("SELECT id, name, email, role FROM users WHERE id = ?", (user_id,)).fetchone() if user_id else None


@bp.route("/cadastro", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("projects.dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "")
        errors = []
        if not 2 <= len(name) <= 100:
            errors.append("Informe seu nome com 2 a 100 caracteres.")
        if not valid_email(email):
            errors.append("Informe um e-mail válido.")
        if not 8 <= len(password) <= 128:
            errors.append("A senha precisa ter entre 8 e 128 caracteres.")
        if password != request.form.get("confirm_password", ""):
            errors.append("As senhas não são iguais.")
        if role not in {"aluno", "professor"}:
            errors.append("Selecione aluno ou professor.")
        if not errors:
            connection = get_db()
            try:
                connection.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                                   (name, email, generate_password_hash(password), role))
                connection.commit()
                flash("Conta criada! Entre para cadastrar seu primeiro projeto.", "success")
                return redirect(url_for("auth.login"))
            except sqlite3.IntegrityError:
                connection.rollback()
                errors.append("Já existe uma conta com esse e-mail.")
        return render_template("auth/register.html", errors=errors, form=request.form), 400
    return render_template("auth/register.html", errors=[], form={})


@bp.route("/entrar", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("projects.dashboard"))
    if request.method == "POST":
        connection = get_db()
        ip = request.remote_addr or "unknown"
        now = int(time.time())
        connection.execute("DELETE FROM login_attempts WHERE attempted_at < ?", (now - 900,))
        count = connection.execute("SELECT COUNT(*) FROM login_attempts WHERE remote_addr = ?", (ip,)).fetchone()[0]
        connection.commit()
        if count >= 10:
            abort(429)
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and len(password) <= 128 and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session.permanent = True
            connection.execute("DELETE FROM login_attempts WHERE remote_addr = ?", (ip,))
            connection.commit()
            flash("Você entrou na Vitrine Virtual.", "success")
            return redirect(url_for("projects.dashboard"))
        connection.execute("INSERT INTO login_attempts (remote_addr, attempted_at) VALUES (?, ?)", (ip, now))
        connection.commit()
        return render_template("auth/login.html", errors=["E-mail ou senha incorretos."], form=request.form), 400
    return render_template("auth/login.html", errors=[], form={})


@bp.post("/sair")
def logout():
    session.clear()
    flash("Sessão encerrada.", "success")
    return redirect(url_for("projects.index"))
