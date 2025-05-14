from datetime import datetime
# from telegram_bot.config import database_url
from sqlalchemy import func, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

DATABASE_URL = f"postgresql+asyncpg://postgres:Fotefi25+@localhost:5432/postgres"
# DATABASE_URL = 'amvera-nastena-555-cnpg-sheese-factory-rw'
# Создание асинхронного движка для подключения к БД
engine = create_async_engine(url=DATABASE_URL)

# Создание фабрики сессий
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# Базовый класс для моделей
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  # Этот класс не будет создавать отдельную таблицу

    # Общее поле "id" для всех таблиц
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Поля времени создания и обновления записи
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Функция для автоматического определения имени таблицы
        :return: имя таблицы
        """
        return cls.__name__.lower() + 's'

    def to_dict(self) -> dict:
        """
        Метод для преобразования объекта в словарь
        :return: словарь, полученный из таблицы
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}