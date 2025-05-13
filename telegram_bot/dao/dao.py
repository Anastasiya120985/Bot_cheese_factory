from datetime import datetime, timedelta
from typing import Optional, List, Dict
from loguru import logger
from sqlalchemy import select, func, case
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from telegram_bot.dao.base import BaseDAO
from telegram_bot.dao.models import User, Purchase, Category, Product, Cart


class UserDAO(BaseDAO[User]):
    model = User

    @classmethod
    async def get_purchase_statistics(cls, session: AsyncSession, telegram_id: int) -> Optional[Dict[str, int]]:
        """
        Асинхронный метод возвращает общее количество покупок и их сумму для конкретного пользователя по его Telegram ID
        :param session: асинхронная сессия базы данных
        :param telegram_id: Telegram ID пользователя
        :return: общее количество покупок и общая сумма покупок пользователя
        """
        try:
            result = await session.execute(
                select(
                    func.count(Purchase.id).label('total_purchases'),
                    func.sum(Purchase.price).label('total_amount')
                ).join(User).filter(User.telegram_id == telegram_id)
            )
            stats = result.one_or_none()

            if stats is None:
                return None

            total_purchases, total_amount = stats
            return {
                'total_purchases': total_purchases,
                'total_amount': total_amount or 0
            }

        except SQLAlchemyError as e:
            print(f"Ошибка при получении статистики покупок пользователя: {e}")
            return None

    @classmethod
    async def get_purchased_products(cls, session: AsyncSession, telegram_id: int) -> Optional[List[Purchase]]:
        """
        Асинхронный метод возвращает список всех покупок пользователя с детализацией по продуктам
        :param session: асинхронная сессия базы данных
        :param telegram_id: Telegram ID пользователя
        :return: список с покупками пользователь
        """
        try:
            result = await session.execute(
                select(User)
                .options(
                    selectinload(User.purchases).selectinload(Purchase.product)
                )
                .filter(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                return None

            return user.purchases

        except SQLAlchemyError as e:
            print(f"Ошибка при получении информации о покупках пользователя: {e}")
            return None

    @classmethod
    async def get_statistics(cls, session: AsyncSession):
        """
        Асинхронный метод собирает данные о количестве пользователей, зарегистрированных за различные временные периоды
        :param session: асинхронная сессия базы данных
        :return: статистика по пользователям во временной разбивке
        """
        try:
            now = datetime.now()

            query = select(
                func.count().label('total_users'),
                func.sum(case((cls.model.created_at >= now - timedelta(days=1), 1), else_=0)).label('new_today'),
                func.sum(case((cls.model.created_at >= now - timedelta(days=7), 1), else_=0)).label('new_week'),
                func.sum(case((cls.model.created_at >= now - timedelta(days=30), 1), else_=0)).label('new_month')
            )

            result = await session.execute(query)
            stats = result.fetchone()

            statistics = {
                'total_users': stats.total_users,
                'new_today': stats.new_today,
                'new_week': stats.new_week,
                'new_month': stats.new_month
            }

            logger.info(f"Статистика успешно получена: {statistics}")
            return statistics
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            raise


class CategoryDao(BaseDAO[Category]):
    model = Category


class ProductDao(BaseDAO[Product]):
    model = Product


class CartDao(BaseDAO[Cart]):
    model = Cart


class PurchaseDao(BaseDAO[Purchase]):
    model = Purchase

    @classmethod
    async def get_full_summ(cls, session: AsyncSession) -> int:
        """
        Асинхронный метод для подсчета общей суммы всех покупок
        :param session: асинхронная сессия базы данных
        :return: общая сумма покупок
        """
        query = select(func.sum(cls.model.price).label('total_price'))
        result = await session.execute(query)
        total_price = result.scalars().one_or_none()
        return total_price if total_price is not None else 0