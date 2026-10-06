"""Validações compartilhadas; todos os dados também são validados no servidor."""
import re
from urllib.parse import urlsplit

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
CATEGORIES = ("Ensino", "Pesquisa", "Extensão")
COURSES = ("Análise e Desenvolvimento de Sistemas", "Técnico em Informática", "Técnico em Meio Ambiente", "Técnico em Agropecuária")
AREAS = ("Computação", "Educação", "Ciências Ambientais", "Ciências Agrárias", "Saúde", "Ciências Humanas", "Engenharias")


def valid_email(value):
    return len(value) <= 254 and bool(EMAIL_PATTERN.fullmatch(value))


def valid_url(value):
    if not value:
        return True
    try:
        parsed = urlsplit(value)
        return (len(value) <= 1000 and parsed.scheme in {"https", "http"}
                and bool(parsed.hostname) and parsed.username is None and parsed.password is None
                and not any(c.isspace() or ord(c) < 32 for c in value))
    except ValueError:
        return False


def project_data(form):
    limits = {"title": 160, "course": 120, "area": 100, "summary": 1000,
              "description": 15000, "results": 15000, "team": 1000,
              "advisor": 200, "contact_email": 254, "contact_phone": 40,
              "repository_url": 1000, "external_url": 1000}
    data = {field: form.get(field, "").strip() for field in limits}
    errors = []
    labels = {"title": "Título", "course": "Curso", "area": "Área do conhecimento",
              "summary": "Resumo", "team": "Equipe responsável"}
    for field, label in labels.items():
        if not data[field]:
            errors.append(f"Preencha o campo {label.lower()}.")
    for field, limit in limits.items():
        if len(data[field]) > limit:
            errors.append(f"O campo {labels.get(field, field)} permite até {limit} caracteres.")
    try:
        data["year"] = int(form.get("year", ""))
        if not 1900 <= data["year"] <= 2100:
            raise ValueError
    except ValueError:
        data["year"] = form.get("year", "")
        errors.append("Informe um ano entre 1900 e 2100.")
    data["category"] = form.get("category", "")
    data["status"] = form.get("status", "draft")
    if data["category"] not in CATEGORIES:
        errors.append("Escolha ensino, pesquisa ou extensão.")
    if data["status"] not in {"draft", "published"}:
        errors.append("Escolha uma situação válida para o projeto.")
    if data["contact_email"] and not valid_email(data["contact_email"]):
        errors.append("Informe um e-mail de contato válido.")
    for field in ("repository_url", "external_url"):
        if not valid_url(data[field]):
            errors.append("Os links precisam ser endereços completos iniciados por https:// ou http://.")
    if data["contact_phone"] and not re.fullmatch(r"[+\d() .-]{8,40}", data["contact_phone"]):
        errors.append("Informe um telefone válido com DDD.")
    return data, errors
