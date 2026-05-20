# Контрольная работа №3 — FastAPI

## Установка

```bash
cd kr3
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
```

Скопируйте `.env.example` в `.env` и при необходимости измените значения.

## Запуск

```bash
uvicorn main:app --reload
```

## Тесты

```bash
pytest tests -v
```

Тесты используют отдельную временную базу SQLite и не трогают `app.db`.

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| MODE | `DEV` или `PROD` |
| DOCS_USER | логин для `/docs` в режиме DEV |
| DOCS_PASSWORD | пароль для `/docs` в режиме DEV |
| JWT_SECRET | секрет для JWT |

## Примеры curl

### 6.1–6.2 Basic Auth

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"user1\",\"password\":\"pass123\"}" http://127.0.0.1:8000/register
curl -u user1:pass123 http://127.0.0.1:8000/login
```

### 6.3 Документация

```bash
curl -u admin:secret http://127.0.0.1:8000/docs
set MODE=PROD
curl http://127.0.0.1:8000/docs
```

### 6.4–6.5 JWT

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"alice\",\"password\":\"qwerty123\"}" http://127.0.0.1:8000/register
curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"alice\",\"password\":\"qwerty123\"}" http://127.0.0.1:8000/login
curl -H "Authorization: Bearer <TOKEN>" http://127.0.0.1:8000/protected_resource
```

### 7.1 RBAC

При регистрации можно указать роль: `admin`, `user`, `guest`.

```bash
curl -X POST -H "Content-Type: application/json" -d "{\"username\":\"bob\",\"password\":\"123\",\"role\":\"guest\"}" http://127.0.0.1:8000/register
```

### 8.1 SQLite

```bash
curl -X POST http://127.0.0.1:8000/register -H "Content-Type: application/json" -d "{\"username\":\"test_user\",\"password\":\"12345\",\"role\":\"user\"}"
```

### 8.2 Todo CRUD

```bash
curl -X POST http://127.0.0.1:8000/todos -H "Content-Type: application/json" -d "{\"title\":\"Buy groceries\",\"description\":\"Milk, eggs, bread\"}"
curl http://127.0.0.1:8000/todos/1
curl -X PUT http://127.0.0.1:8000/todos/1 -H "Content-Type: application/json" -d "{\"title\":\"Buy groceries\",\"description\":\"Milk\",\"completed\":true}"
curl -X DELETE http://127.0.0.1:8000/todos/1
```
