import io
from pathlib import Path
from vitrine.db import get_db
from conftest import project_payload, token
from test_system import create_project, image_file


def test_invalid_second_image_rolls_back_all_uploads(logged_client, app):
    images = [image_file(), (io.BytesIO(b"arquivo sem imagem"), "invalida.png")]
    response = logged_client.post("/projetos/novo", data=project_payload(logged_client, images=images))
    assert response.status_code == 400
    assert list(Path(app.config["UPLOAD_FOLDER"]).iterdir()) == []
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0
        assert get_db().execute("SELECT COUNT(*) FROM project_images").fetchone()[0] == 0


def test_unpublishing_revokes_public_project_and_image_access(logged_client, app):
    project_id = create_project(logged_client, images=image_file())
    with app.app_context():
        filename = get_db().execute("SELECT filename FROM project_images").fetchone()[0]
    visitor = app.test_client()
    assert visitor.get(f"/imagens/{filename}").status_code == 200
    response = logged_client.post(f"/projetos/{project_id}/editar", data=project_payload(logged_client, status="draft"))
    assert response.status_code == 302
    assert visitor.get(f"/projetos/{project_id}").status_code == 404
    assert visitor.get(f"/imagens/{filename}").status_code == 404
    assert logged_client.get(f"/imagens/{filename}").status_code == 200
