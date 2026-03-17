# TeamFinder

Платформа для поиска участников в pet-проекты. Зарегистрированные пользователи могут публиковать идеи проектов, находить команду и откликаться на опубликованные предложения.

Реализован вариант 3: навыки проектов и фильтрация по навыкам.

## Функциональность

- Регистрация и аутентификация пользователей (по email и паролю)
- Публичные профили пользователей с контактами и списком проектов
- Создание, редактирование и завершение проектов
- Участие в проектах других пользователей
- Добавление проектов в избранное
- Навыки проектов с автодополнением — добавление и удаление без перезагрузки страницы
- Фильтрация проектов по навыкам
- Смена пароля
- Генерация аватара при регистрации

## Стек технологий

- Python 3.13
- Django 5.2
- PostgreSQL 16
- Docker / Docker Compose
- Pillow

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

### 5. Тестовые данные
```bash
python manage.py seed_data
```

Создаёт 3 тестовых пользователя с проектами:

| Email | Пароль |
|---|---|
| alice@example.com | testpass123 |
| bob@example.com | testpass123 |
| carol@example.com | testpass123 |

### 6. Админка
```bash
python manage.py createsuperuser
```

Админка доступна по адресу: http://localhost:8000/admin/

## Автор

Кузьмин Кирилл, студент группы 8К23, ТПУ