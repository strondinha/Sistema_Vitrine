"""Conexão SQLite por requisição e comandos administrativos."""
import sqlite3
import secrets
import unicodedata
import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], timeout=15)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        # Busca em português, ignorando maiúsculas e acentos.
        g.db.create_function("fold_text", 1, fold_text, deterministic=True)
    return g.db


def fold_text(value):
    return "".join(char for char in unicodedata.normalize("NFKD", value or "") if not unicodedata.combining(char)).casefold()


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    with current_app.open_resource("schema.sql") as source:
        get_db().executescript(source.read().decode("utf-8"))


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Cria as tabelas ausentes sem excluir os registros existentes."""
    init_db()
    click.echo("Banco de dados preparado. Registros existentes foram preservados.")


@click.command("seed-demo")
@with_appcontext
def seed_demo():
    """Adiciona exemplos fictícios para demonstração, sem senha pública."""
    connection = get_db()
    if connection.execute("SELECT id FROM users WHERE email = ?", ("demo@vitrine.local",)).fetchone():
        click.echo("Os exemplos de demonstração já foram carregados.")
        return
    author = connection.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ("Equipe de demonstração", "demo@vitrine.local", generate_password_hash(secrets.token_urlsafe(32)), "professor"),
    ).lastrowid
    examples = [
        ("Tecnologia que aproxima", "Análise e Desenvolvimento de Sistemas", "Computação", "Extensão", "Uma proposta de oficina de inclusão digital para a comunidade de Corrente.", "Oficinas introdutórias sobre uso do computador, serviços digitais e navegação segura.", "Resultados ilustrativos: materiais de apoio e roteiro de oficinas disponíveis para discussão."),
        ("Água e comunidade", "Técnico em Meio Ambiente", "Ciências Ambientais", "Pesquisa", "Estudo demonstrativo sobre saneamento e qualidade de vida na região.", "Levantamento de informações e construção de indicadores para aproximar pesquisa e comunidade.", "Resultados ilustrativos: diagnóstico inicial e proposta de ações educativas."),
        ("Aprender programação na prática", "Análise e Desenvolvimento de Sistemas", "Educação", "Ensino", "Uma sequência de atividades para aprender lógica de programação com pequenos projetos.", "Exercícios progressivos e encontros de aprendizagem colaborativa.", "Resultados ilustrativos: conjunto de exercícios e sugestões para atividades em sala."),
    ]
    for title, course, area, category, summary, description, results in examples:
        connection.execute(
            """INSERT INTO projects (user_id, title, course, area, year, category, summary,
            description, results, team, advisor, contact_email, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'published')""",
            (author, title + " — exemplo", course, area, 2026, category, summary, description,
             results, "Equipe fictícia de demonstração", "Orientação de demonstração", "",),
        )
    connection.commit()
    click.echo("3 projetos fictícios adicionados. Crie sua própria conta para publicar projetos reais.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_demo)
