import io
from pathlib import Path
import pytest
from PIL import Image
from werkzeug.security import check_password_hash
from vitrine import create_app
from vitrine.db import get_db
from conftest import login, project_payload, register, token


def image_file(name="foto.png"):
    data = io.BytesIO()
    Image.new("RGB", (200, 120), "green").save(data, format="PNG")
    data.seek(0)
    return data, name


def create_project(client, **overrides):
    response = client.post("/projetos/novo", data=project_payload(client, **overrides))
    assert response.status_code == 302
    return int(response.headers["Location"].split("/")[-1])


def test_public_pages_and_empty_catalog(client):
    for path in ("/", "/sobre", "/conta/entrar", "/conta/cadastro"):
        response = client.get(path)
        assert response.status_code == 200
        assert b'lang="pt-BR"' in response.data
    assert "A próxima ideia pode ser a sua" in client.get("/").text
    assert client.get("/inexistente").status_code == 404


def test_registration_login_and_logout(client, app):
    assert register(client).status_code == 302
    with app.app_context():
        user = get_db().execute("SELECT * FROM users").fetchone()
        assert user["password_hash"] != "SenhaTeste123"
        assert check_password_hash(user["password_hash"], "SenhaTeste123")
    assert login(client).status_code == 302
    assert client.get("/meus-projetos").status_code == 200
    assert client.post("/conta/sair", data={"csrf_token": token(client)}).status_code == 302
    assert client.get("/meus-projetos").status_code == 302


def test_duplicate_email_is_case_insensitive(client):
    register(client)
    assert register(client, email="CAIO@example.com").status_code == 400


def test_invalid_account_data(client):
    response = client.post("/conta/cadastro", data={"csrf_token": token(client), "name": "A", "email": "errado", "password": "123", "role": "admin"})
    assert response.status_code == 400
    assert "senhas não são iguais" in response.text


def test_invalid_password_and_throttling(client):
    register(client)
    data = {"csrf_token": token(client), "email": "caio@example.com", "password": "incorreta"}
    for _ in range(10):
        assert client.post("/conta/entrar", data=data).status_code == 400
    assert client.post("/conta/entrar", data=data).status_code == 429


@pytest.mark.parametrize("path", ["/conta/cadastro", "/conta/entrar", "/conta/sair", "/projetos/novo"])
def test_posts_require_csrf(client, path):
    assert client.post(path, data={}).status_code == 400
    assert client.post(path, data={"csrf_token": "á-é-ç"}).status_code == 400


def test_project_crud(logged_client, app):
    project_id = create_project(logged_client)
    detail = logged_client.get(f"/projetos/{project_id}")
    assert "Resultados alcançados" in detail.text
    assert "equipe@example.com" in detail.text
    assert "https://github.com/exemplo/projeto" in detail.text
    assert "Soluções para Corrente" in logged_client.get("/").text
    assert logged_client.post(f"/projetos/{project_id}/editar", data=project_payload(logged_client, title="Novo título")).status_code == 302
    assert "Novo título" in logged_client.get(f"/projetos/{project_id}").text
    assert logged_client.post(f"/projetos/{project_id}/excluir", data={"csrf_token": token(logged_client)}).status_code == 302
    assert logged_client.get(f"/projetos/{project_id}").status_code == 404
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0


def test_draft_is_private_and_can_be_published(logged_client, app):
    project_id = create_project(logged_client, status="draft", images=image_file())
    guest = app.test_client()
    assert "Soluções para Corrente" not in guest.get("/").text
    assert guest.get(f"/projetos/{project_id}").status_code == 404
    with app.app_context():
        filename = get_db().execute("SELECT filename FROM project_images").fetchone()[0]
    assert guest.get(f"/imagens/{filename}").status_code == 404
    assert logged_client.get(f"/imagens/{filename}").status_code == 200
    assert logged_client.get(f"/projetos/{project_id}").status_code == 200
    logged_client.post(f"/projetos/{project_id}/editar", data=project_payload(logged_client))
    assert guest.get(f"/projetos/{project_id}").status_code == 200
    assert guest.get(f"/imagens/{filename}").status_code == 200


def test_only_owner_can_modify_project(logged_client, app):
    project_id = create_project(logged_client)
    other = app.test_client()
    register(other, email="outra@example.com", name="Outra pessoa")
    login(other, email="outra@example.com")
    assert other.get(f"/projetos/{project_id}/editar").status_code == 403
    assert other.post(f"/projetos/{project_id}/editar", data=project_payload(other)).status_code == 403
    assert other.post(f"/projetos/{project_id}/excluir", data={"csrf_token": token(other)}).status_code == 403
    assert logged_client.get(f"/projetos/{project_id}").status_code == 200


def test_anonymous_cannot_create(client):
    assert client.get("/projetos/novo").status_code == 302
    assert client.post("/projetos/novo", data=project_payload(client)).status_code == 302


def test_search_and_combined_filters(logged_client):
    create_project(logged_client)
    create_project(logged_client, title="Horta comunitária", course="Agropecuária", area="Ciências Agrárias", year="2025", category="Pesquisa")
    result = logged_client.get("/", query_string={"q": "SOLUCOES", "course": "Análise e Desenvolvimento de Sistemas", "area": "Computação", "year": "2026", "category": "Extensão"})
    assert "Soluções para Corrente" in result.text
    assert "Horta comunitária" not in result.text
    assert "Nenhum projeto com esses filtros" in logged_client.get("/?q=inexistente").text
    assert "Horta comunitária" in logged_client.get("/?q=horta").text


def test_search_wildcards_are_literal_and_sql_is_parameterized(logged_client):
    create_project(logged_client)
    assert "Nenhum projeto com esses filtros" in logged_client.get("/?q=%25").text
    assert "Nenhum projeto com esses filtros" in logged_client.get("/", query_string={"q": "' OR 1=1 --"}).text


def test_pagination_preserves_filters(logged_client):
    for index in range(11):
        create_project(logged_client, title=f"Projeto paginado {index}")
    first = logged_client.get("/?year=2026")
    assert first.text.count('class="project-card"') == 9
    assert "year=2026" in first.text
    second = logged_client.get("/?year=2026&page=2")
    assert second.text.count('class="project-card"') == 2
    assert logged_client.get("/?page=abc").status_code == 200


@pytest.mark.parametrize("overrides", [
    {"title": ""}, {"year": "banana"}, {"year": "2200"}, {"category": "Outro"},
    {"repository_url": "javascript:alert(1)"}, {"external_url": "https://usuario:senha@site.com"},
    {"status": "admin"}, {"contact_email": "inválido"}, {"contact_phone": "texto errado"},
])
def test_invalid_project_data_is_rejected(logged_client, app, overrides):
    assert logged_client.post("/projetos/novo", data=project_payload(logged_client, **overrides)).status_code == 400
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0


def test_stored_html_is_escaped(logged_client):
    project_id = create_project(logged_client, title="<script>alert('x')</script>", description="<img src=x onerror=alert(1)>")
    result = logged_client.get(f"/projetos/{project_id}")
    assert "<script>alert" not in result.text
    assert "&lt;script&gt;" in result.text
    assert "&lt;img" in result.text


def test_upload_sanitization_and_image_removal(logged_client, app):
    project_id = create_project(logged_client, images=image_file("../../foto.png"))
    with app.app_context():
        image = dict(get_db().execute("SELECT * FROM project_images").fetchone())
    assert image["filename"].endswith(".jpg")
    assert "/" not in image["filename"]
    image_path = Path(app.config["UPLOAD_FOLDER"]) / image["filename"]
    assert image_path.exists()
    assert logged_client.get(f"/imagens/{image['filename']}").mimetype == "image/jpeg"
    response = logged_client.post(f"/projetos/{project_id}/editar", data=project_payload(logged_client, remove_images=str(image["id"])))
    assert response.status_code == 302
    assert not image_path.exists()


def test_delete_project_removes_images(logged_client, app):
    project_id = create_project(logged_client, images=image_file())
    logged_client.post(f"/projetos/{project_id}/excluir", data={"csrf_token": token(logged_client)})
    assert list(Path(app.config["UPLOAD_FOLDER"]).iterdir()) == []
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM project_images").fetchone()[0] == 0


def test_fake_image_and_oversize_upload_are_rejected(logged_client, app):
    fake = (io.BytesIO(b"<svg onload='alert(1)'></svg>"), "foto.png")
    assert logged_client.post("/projetos/novo", data=project_payload(logged_client, images=fake)).status_code == 400
    large = (io.BytesIO(b"x" * (5 * 1024 * 1024 + 1)), "grande.jpg")
    assert logged_client.post("/projetos/novo", data=project_payload(logged_client, images=large)).status_code == 400
    too_large = (io.BytesIO(b"x" * (16 * 1024 * 1024 + 1)), "enorme.jpg")
    assert logged_client.post("/projetos/novo", data=project_payload(logged_client, images=too_large)).status_code == 413
    assert list(Path(app.config["UPLOAD_FOLDER"]).iterdir()) == []


def test_image_count_limit(logged_client, app):
    data = project_payload(logged_client, images=[image_file(f"{i}.png") for i in range(7)])
    assert logged_client.post("/projetos/novo", data=data).status_code == 400
    assert list(Path(app.config["UPLOAD_FOLDER"]).iterdir()) == []


def test_cannot_remove_another_projects_image(logged_client, app):
    first = create_project(logged_client, images=image_file())
    second = create_project(logged_client, title="Outro projeto")
    with app.app_context():
        image_id = get_db().execute("SELECT id FROM project_images WHERE project_id = ?", (first,)).fetchone()[0]
    assert logged_client.post(f"/projetos/{second}/editar", data=project_payload(logged_client, remove_images=str(image_id))).status_code == 400


def test_data_persists_after_restart(logged_client, app):
    create_project(logged_client)
    restarted = create_app({"TESTING": True, "SECRET_KEY": app.config["SECRET_KEY"], "DATABASE": app.config["DATABASE"], "UPLOAD_FOLDER": app.config["UPLOAD_FOLDER"]})
    assert "Soluções para Corrente" in restarted.test_client().get("/").text


def test_seed_demo_is_idempotent_and_init_preserves_data(app):
    runner = app.test_cli_runner()
    assert runner.invoke(args=["seed-demo"]).exit_code == 0
    assert runner.invoke(args=["seed-demo"]).exit_code == 0
    assert runner.invoke(args=["init-db"]).exit_code == 0
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 3


def test_security_headers(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "form-action 'self'" in response.headers["Content-Security-Policy"]
    assert client.get("/imagens/arquivo-inexistente.jpg").status_code == 404
