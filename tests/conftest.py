"""Cada teste usa um banco temporário e nunca altera dados reais."""
import pytest
from vitrine import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({
        "TESTING": True,
        "SECRET_KEY": "chave-exclusiva-de-testes",
        "DATABASE": str(tmp_path / "test.sqlite3"),
        "UPLOAD_FOLDER": str(tmp_path / "uploads"),
    })


@pytest.fixture
def client(app):
    return app.test_client()


def token(client):
    client.get("/conta/entrar", follow_redirects=True)
    with client.session_transaction() as session:
        return session["csrf_token"]


def register(client, email="caio@example.com", name="Caio de teste"):
    return client.post("/conta/cadastro", data={
        "csrf_token": token(client), "name": name, "email": email,
        "role": "aluno", "password": "SenhaTeste123", "confirm_password": "SenhaTeste123",
    })


def login(client, email="caio@example.com"):
    return client.post("/conta/entrar", data={"csrf_token": token(client), "email": email, "password": "SenhaTeste123"})


@pytest.fixture
def logged_client(client):
    register(client)
    login(client)
    return client


def project_payload(client, **overrides):
    data = {
        "csrf_token": token(client), "title": "Soluções para Corrente",
        "course": "Análise e Desenvolvimento de Sistemas", "area": "Computação",
        "year": "2026", "category": "Extensão", "summary": "Resumo do projeto de teste.",
        "description": "Descrição completa.", "results": "Resultados alcançados.",
        "team": "Caio e equipe", "advisor": "Professor de teste",
        "contact_email": "equipe@example.com", "contact_phone": "(89) 99999-9999",
        "repository_url": "https://github.com/exemplo/projeto", "external_url": "",
        "status": "published",
    }
    data.update(overrides)
    return data
