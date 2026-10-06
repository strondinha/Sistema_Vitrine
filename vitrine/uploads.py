"""Recebe imagens reais, remove metadados e salva com nome aleatório."""
import io
import uuid
import warnings
from pathlib import Path
from flask import current_app
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGES = 6
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def remove_files(filenames):
    for filename in filenames:
        (Path(current_app.config["UPLOAD_FOLDER"]) / filename).unlink(missing_ok=True)


def save_images(files):
    saved = []
    try:
        for uploaded in files:
            data = uploaded.stream.read(MAX_IMAGE_BYTES + 1)
            if len(data) > MAX_IMAGE_BYTES:
                raise ValueError("Cada imagem deve ter no máximo 5 MB.")
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(data)) as original:
                    if original.format not in {"JPEG", "PNG", "WEBP"}:
                        raise ValueError("Envie somente imagens JPG, PNG ou WEBP.")
                    if original.width * original.height > 20_000_000:
                        raise ValueError("A imagem deve ter no máximo 20 megapixels.")
                    original.load()
                    image = ImageOps.exif_transpose(original).convert("RGB")
                    image.thumbnail((1920, 1920))
                    filename = uuid.uuid4().hex + ".jpg"
                    image.save(Path(current_app.config["UPLOAD_FOLDER"]) / filename, "JPEG", quality=88)
                    saved.append((filename, Path(uploaded.filename).name[:200]))
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        remove_files([item[0] for item in saved])
        raise ValueError("Não foi possível ler uma imagem. Envie um JPG, PNG ou WEBP válido.") from error
    except ValueError:
        remove_files([item[0] for item in saved])
        raise
    return saved
