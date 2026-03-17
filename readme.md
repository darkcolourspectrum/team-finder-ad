# TeamFinder — Вариант 3

Платформа для поиска участников в pet-проекты. Реализован вариант 3: навыки проектов и фильтрация по навыкам.

## Запуск проекта

### 1. Виртуальное окружение

```bash
python -m venv venv
```

Windows (PowerShell):
```bash
venv\Scripts\Activate.ps1
```

Linux/Mac:
```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

### 2. Файл `.env`

```bash
cp .env_example .env
```

Заполнить `.env` следующими значениями:

```
DJANGO_SECRET_KEY=change_for_safety
DJANGO_DEBUG=True
POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
TASK_VERSION=3
```

> **Важно:** порт БД — `5433`, а не стандартный `5432`. Это сделано намеренно, так как порт 5432 может быть занят системным PostgreSQL на Windows. В `docker-compose.yml` прописано `127.0.0.1:5433:5432`.

### 3. База данных

```bash
docker compose up -d
```

### 4. Миграции и запуск

```bash
python manage.py migrate
python manage.py runserver
```

Проект доступен по адресу: http://localhost:8000

### 5. Админка

Для доступа к `/admin/` создать суперпользователя:

```bash
python manage.py createsuperuser
```