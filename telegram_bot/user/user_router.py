from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from telegram_bot.dao.dao import UserDAO
from telegram_bot.user.kbs import main_user_kb
from telegram_bot.user.schemas import TelegramIDModel, UserModel

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession):
    user_id = message.from_user.id
    user_info = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=TelegramIDModel(telegram_id=user_id)
    )

    if user_info:
        return await message.answer(
            f"👋 Добро пожаловать, <b>{message.from_user.first_name}</b>! Выберите необходимое действие:",
            reply_markup=main_user_kb(user_id)
        )

    values = UserModel(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await UserDAO.add(session=session_with_commit, values=values)
    await message.answer(f"🎉 <b>Добро пожаловать!</b>. Теперь выберите необходимое действие:",
                         reply_markup=main_user_kb(user_id))


@user_router.callback_query(F.data == "home")
async def page_home(call: CallbackQuery):
    await call.answer("Главная страница")
    return await call.message.answer(
        f"👋 Добро пожаловать, <b>{call.from_user.first_name}</b>! Выберите необходимое действие:",
        reply_markup=main_user_kb(call.from_user.id)
    )


@user_router.callback_query(F.data == "about")
async def page_about(call: CallbackQuery):
    await call.answer("О магазине")
    image = 'https://disk.yandex.ru/i/048WioGsZ0abKw'
    await call.message.answer_photo(
        photo=image,
        caption=(
            "Добро пожаловать!\n\n"
            "Меня зовут Анастасия, и моя страсть к искусству сыроварения переросла в настоящее призвание. Я с огромным удовольствием представляю вам мой крафтовый сыр, который готовлю с любовью и заботой. 💖 Каждая партия сыра создается из молока наших фермерских коров и коз, которые пасутся на богатых лугах, и это придает нашему сыру неповторимый вкус и качество. 🐄🐐\n\n"           
            "Мы гордимся тем, что все наши продукты обладают 100% натуральным составом✅\n\n"
            "Предлагаем вам окунуться в мир настоящего вкуса, который останется в вашей памяти надолго. Пусть наш сыр станет неотъемлемой частью ваших семейных обедов, перекусов и праздничных столов. 🥂🍽️ Это продукт, который создан, чтобы радовать вас и ваших близких, создавая атмосферу уюта и счастья. 🏡😊\n\n"
            "Приятного аппетита! 🧀✨"
        ),
        reply_markup=main_user_kb(call.from_user.id)
    )