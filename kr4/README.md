# Контрольная работа №4

## Установка

```bash
cd kr4
pip install -r requirements.txt
```

## Миграции (задание 9.1)

```bash
python -m alembic upgrade 001
python seed_products.py
python -m alembic upgrade head
```

Проверка таблицы: `GET /products` после запуска сервера.

## Запуск

```bash
uvicorn main:app --reload
```

## Тесты

```bash
pytest -v
```

## Примеры

```bash
curl "http://127.0.0.1:8000/check-condition?fail=true"
curl http://127.0.0.1:8000/resource/0
curl -X POST http://127.0.0.1:8000/validate-user -H "Content-Type: application/json" -d "{\"username\":\"anna\",\"age\":20,\"email\":\"a@b.ru\",\"password\":\"12345678\"}"
curl -X POST http://127.0.0.1:8000/users -H "Content-Type: application/json" -d "{\"username\":\"test\",\"age\":25}"
```
