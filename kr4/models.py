from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[float] = mapped_column(Float)
    count: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
