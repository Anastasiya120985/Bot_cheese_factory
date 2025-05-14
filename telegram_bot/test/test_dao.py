import unittest
from telegram_bot.dao.dao import UserDAO, PurchaseDao

#
# class TestUserDAO(unittest.TestCase):
#     async def test_get_purchase_statistics(self):
#         users = get_purchase_statistics()
#         for u in users:
#             if u.telegram_id == '1111111':
#                  '1111111' = u
#                  break
#          else:
#              raise AssertionError
#          t = UserDAO('')
#          self.assertEqual(t.total_purchases, moscow.name)
#          self.assertEqual(t.total_amount, moscow.country)
#
#
# async def get_purchase_statistics(cls, session: AsyncSession, telegram_id: int) -> Optional[Dict[str, int]]:
#     """
#     Асинхронный метод возвращает общее количество покупок и их сумму для конкретного пользователя по его Telegram ID
#     :param session: асинхронная сессия базы данных
#     :param telegram_id: Telegram ID пользователя
#     :return: общее количество покупок и общая сумма покупок пользователя
#     """
#     try:
#         result = await session.execute(
#             select(
#                 func.count(Purchase.id).label('total_purchases'),
#                 func.sum(Purchase.price).label('total_amount')
#             ).join(User).filter(User.telegram_id == telegram_id)
#         )
#         stats = result.one_or_none()
#
#         if stats is None:
#             return None
#
#         total_purchases, total_amount = stats
#         return {
#             'total_purchases': total_purchases,
#             'total_amount': total_amount or 0
#         }
#
#     except SQLAlchemyError as e:
#         print(f"Ошибка при получении статистики покупок пользователя: {e}")
#         return None