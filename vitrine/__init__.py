"""Configuração da Vitrine Virtual e registro dos módulos."""
import os
import secrets
from pathlib import Path
from datetime import timedelta
from flask import Flask, render_template, session


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.config.from_mapping(
        DATABASE=str(Path(app.instance_path) / "vitrine.sqlite3"),
        UPLOAD_FOLDER=str(Path(app.instance_path) / "uploads"),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        # A chave persiste entre reinicializações, mas não acompanha o ZIP.
        key_path = Path(app.instance_path) / "secret.key"
        if not key_path.exists():
            try:
                with key_path.open("x") as key_file:
                    key_file.write(secrets.token_hex(32))
                key_path.chmod(0o600)
            except FileExistsError:
                pass
        app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or key_path.read_text().strip()
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    from . import db, security, auth, projects, pages
    db.init_app(app)
    security.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(pages.bp)
    with app.app_context():
        db.init_db()

    @app.template_filter("date_br")
    def date_br(value):
        return "/".join(value[:10].split("-")[::-1]) if value else ""

    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(413)
    @app.errorhandler(429)
    def expected_error(error):
        messages = {
            400: "A solicitação não é válida. Atualize a página e tente novamente.",
            403: "Você não tem permissão para acessar este conteúdo.",
            404: "Não encontramos a página ou o projeto que você procura.",
            413: "O envio ultrapassou 16 MB. Escolha imagens menores e tente novamente.",
            429: "Muitas tentativas de acesso. Aguarde 15 minutos e tente novamente.",
        }
        return render_template("error.html", code=error.code, message=messages[error.code]), error.code

    @app.after_request
    def headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        )
        if "user_id" in session:
            response.headers["Cache-Control"] = "no-store"
        return response

    return app
