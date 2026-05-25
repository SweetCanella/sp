# Контрольная работа №5

FastAPI-приложение с задачами, WebSocket-чатом, Docker-контейнеризацией
и модульной архитектурой с зависимостями.

## Структура

```
app/
  main.py                # точка входа FastAPI
  dependencies.py        # get_current_user, require_admin, get_storage
  schemas.py             # Pydantic-модели
  storage.py             # хранилище задач в памяти
  ws_manager.py          # RoomManager для WebSocket
  routers/
    tasks.py             # /tasks
    users.py             # /users
    admin.py             # /admin
    ws.py                # /ws/rooms/{room_id} и /rooms/{room_id}/users
tests/
  test_tasks.py
  test_health.py
  test_websocket.py
  test_dependencies_and_routing.py
Dockerfile
docker-compose.yml
.dockerignore
requirements.txt
```

## Локальный запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

## Тесты

```bash
pytest -v
```

## Запуск в Docker

```bash
docker compose up --build
```

После запуска:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/tasks -H "X-User-Id: 10"
```

## Авторизация

Все запросы к `/tasks`, `/users`, `/admin` требуют заголовок:

```
X-User-Id: 10
X-User-Role: user   # или admin
```

## Примеры

### Задачи

```bash
curl -X POST http://localhost:8000/tasks \
  -H "X-User-Id: 10" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Подготовить тесты\",\"priority\":4}"

curl http://localhost:8000/tasks -H "X-User-Id: 10"
curl http://localhost:8000/tasks/1 -H "X-User-Id: 10"

curl -X PATCH http://localhost:8000/tasks/1/status \
  -H "X-User-Id: 10" \
  -H "Content-Type: application/json" \
  -d "{\"status\":\"done\"}"

curl -X DELETE http://localhost:8000/tasks/1 -H "X-User-Id: 10"
```

### Админ

```bash
curl http://localhost:8000/admin/stats -H "X-User-Id: 1" -H "X-User-Role: admin"
curl -X DELETE http://localhost:8000/admin/tasks/1 -H "X-User-Id: 1" -H "X-User-Role: admin"
```

### WebSocket

```
ws://localhost:8000/ws/rooms/python?username=alice
```

Отправить:
```json
{"type": "message", "text": "Всем привет"}
```

Получить список пользователей:
```bash
curl http://localhost:8000/rooms/python/users
```
