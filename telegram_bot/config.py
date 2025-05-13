import os
from typing import List
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from pydantic_settings import BaseSettings, SettingsConfigDict

parent_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))


class Settings(BaseSettings):
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"
    model_config = SettingsConfigDict(
        env_file=os.path.join(parent_dir, ".env"), env_file_encoding="utf-8"
    )
    BOT_TOKEN: str
    ADMIN_IDS: List[int]
    PROVIDER_TOKEN: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    def get_db_url(self):
        """
        Метод для получения пути поключения к БД
        :return: URL подключения к базе данных PostgreSQL через aiosqlite
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
admins = settings.ADMIN_IDS

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
logger.add(log_file_path, format=settings.FORMAT_LOG, level="INFO", rotation=settings.LOG_ROTATION)
database_url = settings.get_db_url()



