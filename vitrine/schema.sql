-- Tabelas criadas sem apagar os dados a cada execução.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('aluno', 'professor')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    course TEXT NOT NULL,
    area TEXT NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    category TEXT NOT NULL CHECK (category IN ('Ensino', 'Pesquisa', 'Extensão')),
    summary TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    results TEXT NOT NULL DEFAULT '',
    team TEXT NOT NULL,
    advisor TEXT NOT NULL DEFAULT '',
    contact_email TEXT NOT NULL DEFAULT '',
    contact_phone TEXT NOT NULL DEFAULT '',
    repository_url TEXT NOT NULL DEFAULT '',
    external_url TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL CHECK (status IN ('draft', 'published')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE TABLE IF NOT EXISTS project_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    filename TEXT NOT NULL UNIQUE,
    original_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    remote_addr TEXT NOT NULL,
    attempted_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_filters ON projects(status, course, area, year);
CREATE INDEX IF NOT EXISTS idx_images_project ON project_images(project_id);
CREATE INDEX IF NOT EXISTS idx_attempts_ip ON login_attempts(remote_addr, attempted_at);
