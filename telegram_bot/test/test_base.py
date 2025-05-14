import unittest
from telegram_bot.dao.base import BaseDAO

#
#  class TestBaseDAO(unittest.TestCase):
#
#      async def test_count(self):
#          bases = count()
#          for b in bases:
#              if b.name == 'Moscow':
# #                 moscow = c
# #                 break
# #         else:
# #             raise AssertionError
# #         t = capital('Moscow')
# #         self.assertEqual(t.name, moscow.name)
# #         self.assertEqual(t.country, moscow.country)
# #         self.assertEqual(t.info, moscow.info)
#
#     async def count(cls, session: AsyncSession, filters: BaseModel | None = None):
#         """
#         Асинхронный метод подсчета количества записей
#         :param session: асинхронная сессия базы данных
#         :param filters: словарь фильтров для поиска
#         :return: количество запесей по указанному фильтру
#         """
#         filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
#         logger.info(f"Подсчет количества записей {cls.model.__name__} по фильтру: {filter_dict}")
#         try:
#             query = select(func.count(cls.model.id)).filter_by(**filter_dict)
#             result = await session.execute(query)
#             count = result.scalar()
#             logger.info(f"Найдено {count} записей.")
#             return count
#         except SQLAlchemyError as e:
#             logger.error(f"Ошибка при подсчете записей: {e}")
#             raise