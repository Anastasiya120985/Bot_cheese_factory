import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeAllPrivateChats
from loguru import logger
from telegram_bot.config import bot, admins, dp
from telegram_bot.dao.database_middleware import DatabaseMiddlewareWithoutCommit, DatabaseMiddlewareWithCommit
from telegram_bot.admin.admin import admin_router
from telegram_bot.user.user_router import user_router
from telegram_bot.user.catalog_router import catalog_router


# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    # await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Функция, которая выполнится, когда бот запустится
async def start_bot():
    await set_commands()
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f'Я запущен🥳.')
        except:
            pass
    logger.info("Бот успешно запущен.")


# Функция, которая выполнится, когда бот завершит свою работу
async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, f'Бот остановлен. За что?😔')
    except:
        pass
    logger.error("Бот остановлен!")


async def main():
    # Регистрация мидлварей
    dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    dp.update.middleware.register(DatabaseMiddlewareWithCommit())

    # Регистрация роутеров
    dp.include_router(catalog_router)
    dp.include_router(user_router)
    dp.include_router(admin_router)

    # Регистрация функций
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    # Запуск бота в режиме long polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.delete_my_commands()
        # await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())