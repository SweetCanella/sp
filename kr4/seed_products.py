"""Добавить 2 записи после миграции 001 (задание 9.1)."""
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///./products.db", connect_args={"check_same_thread": False})


def seed():
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
        if count >= 2:
            print("Записи уже есть")
            return

        conn.execute(
            text("INSERT INTO products (title, price, count) VALUES (:t, :p, :c)"),
            {"t": "Phone", "p": 29999.0, "c": 5},
        )
        conn.execute(
            text("INSERT INTO products (title, price, count) VALUES (:t, :p, :c)"),
            {"t": "Book", "p": 499.0, "c": 20},
        )
        conn.commit()
        print("Добавлено 2 товара")


if __name__ == "__main__":
    seed()
