import asyncio
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from telegram_bot.config import admins, bot
from telegram_bot.dao.dao import UserDAO, ProductDao, CategoryDao, PurchaseDao
from telegram_bot.admin.kbs import admin_kb, admin_kb_back, product_management_kb, cancel_kb_inline, catalog_admin_kb, \
    admin_send_file_kb, admin_confirm_kb, dell_change_product_kb, change_product_kb
from telegram_bot.admin.schemas import ProductModel, ProductIDModel
from telegram_bot.admin.utils import process_dell_text_msg

admin_router = Router()


class AddProduct(StatesGroup):
    name = State()
    description = State()
    min_packing = State()
    price = State()
    image = State()
    category_id = State()
    confirm_add = State()


# Функция, которая будет выполняться при входе в админ панель
@admin_router.callback_query(F.data == "admin_panel", F.from_user.id.in_(admins))
async def start_admin(call: CallbackQuery):
    await call.answer('Доступ в админ-панель разрешен!')
    await call.message.edit_text(
        text="Вам разрешен доступ в админ-панель. Выберите необходимое действие.",
        reply_markup=admin_kb()
    )


# Метод, который будет возвращать статистику по боту
@admin_router.callback_query(F.data == 'statistic', F.from_user.id.in_(admins))
async def admin_statistic(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Запрос на получение статистики...')
    await call.answer('📊 Собираем статистику...')

    stats = await UserDAO.get_statistics(session=session_without_commit)
    total_summ = await PurchaseDao.get_full_summ(session=session_without_commit)
    stats_message = (
        "📈 Статистика пользователей:\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"🆕 Новых за сегодня: {stats['new_today']}\n"
        f"📅 Новых за неделю: {stats['new_week']}\n"
        f"📆 Новых за месяц: {stats['new_month']}\n\n"
        f"💰 Общая сумма заказов: {total_summ} руб.\n\n"
        "🕒 Данные актуальны на текущий момент."
    )
    await call.message.edit_text(
        text=stats_message,
        reply_markup=admin_kb()
    )


@admin_router.callback_query(F.data == 'process_products', F.from_user.id.in_(admins))
async def admin_process_products(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим управления товарами')
    all_products_count = await ProductDao.count(session=session_without_commit)
    await call.message.edit_text(
        text=f"На данный момент в базе данных {all_products_count} товаров. Что будем делать?",
        reply_markup=product_management_kb()
    )


@admin_router.callback_query(F.data == 'delete_product', F.from_user.id.in_(admins))
async def admin_process_start_dell_change(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим удаления товаров')
    all_products = await ProductDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text=f"На данный момент в базе данных {len(all_products)} товаров. Для удаления нажмите на кнопку ниже"
    )
    for product_data in all_products:
        image = product_data.image
        product_text = (f'🛒 Описание товара:\n\n'
                        f'🔹 <b>Название товара:</b> {product_data.name}\n'
                        f'🔹 <b>Описание:</b>\n\n{product_data.description}\n\n'
                        f'🔹 <b>Цена:</b> {product_data.price} руб. / {product_data.min_packing}')
        if image:
            await call.message.answer_photo(photo=image, caption=product_text,
                                            reply_markup=dell_change_product_kb(product_data.id))
        else:
            await call.message.answer(text=product_text, reply_markup=dell_change_product_kb(product_data.id))


@admin_router.callback_query(F.data.startswith('dell_'), F.from_user.id.in_(admins))
async def admin_process_start_dell(call: CallbackQuery, session_with_commit: AsyncSession):
    product_id = int(call.data.split('_')[-1])
    await ProductDao.delete(session=session_with_commit, filters=ProductIDModel(id=product_id))
    await call.answer(f"Товар с ID {product_id} удален!", show_alert=True)
    await call.message.delete()


@admin_router.callback_query(F.data.startswith('change_'), F.from_user.id.in_(admins))
async def admin_process_start_change(call: CallbackQuery, session_with_commit: AsyncSession):
    product_id = int(call.data.split('_')[-1])

    product_data = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=product_id)
    image = product_data.image
    product_text = (f'🛒 Описание товара:\n\n'
                    f'🔹 <b>Название товара:</b> {product_data.name}\n'
                    f'🔹 <b>Описание:</b>\n\n{product_data.description}\n\n'
                    f'🔹 <b>Категория:</b>\n\n{product_data.cat}\n\n'
                    f'🔹 <b>Цена:</b> {product_data.price} руб. / {product_data.min_packing}')
    if image:
        await call.message.answer_photo(photo=image, caption=product_text,
                                        reply_markup=change_product_kb())
    else:
        await call.message.answer(text=product_text, reply_markup=change_product_kb())


    await ProductDao.update(session=session_with_commit, filters=ProductIDModel(id=product_id))
    await call.answer(f"Товар с ID {product_id} удален!", show_alert=True)
    await call.message.delete()


#
@admin_router.callback_query(F.data == "cancel", F.from_user.id.in_(admins))
async def admin_process_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer('Отмена сценария добавления товара')
    await call.message.delete()
    await call.message.answer(
        text="Отмена добавления товара.",
        reply_markup=admin_kb_back()
    )


@admin_router.callback_query(F.data == 'add_product', F.from_user.id.in_(admins))
async def admin_process_add_product(call: CallbackQuery, state: FSMContext):
    await call.answer('Запущен сценарий добавления товара.')
    await call.message.delete()
    msg = await call.message.answer(text="Для начала укажите имя товара: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.name)


@admin_router.message(F.text, F.from_user.id.in_(admins), AddProduct.name)
async def admin_process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await process_dell_text_msg(message, state)
    msg = await message.answer(text="Теперь добавьте короткое описание товару: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.description)


@admin_router.message(F.text, F.from_user.id.in_(admins), AddProduct.description)
async def admin_process_description(message: Message, state: FSMContext, session_without_commit: AsyncSession):
    await state.update_data(description=message.html_text)
    await process_dell_text_msg(message, state)
    catalog_data = await CategoryDao.find_all(session=session_without_commit)
    msg = await message.answer(text="Теперь выберите категорию товара: ", reply_markup=catalog_admin_kb(catalog_data))
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.category_id)


@admin_router.callback_query(F.data.startswith("add_category_"),
                             F.from_user.id.in_(admins),
                             AddProduct.category_id)
async def admin_process_category(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split("_")[-1])
    await state.update_data(category_id=category_id)
    await call.answer('Категория товара успешно выбрана.')
    msg = await call.message.edit_text(text="Введите цену товара: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.price)


@admin_router.message(F.text, F.from_user.id.in_(admins), AddProduct.price)
async def admin_process_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        await process_dell_text_msg(message, state)
        msg = await message.answer(
            text="Отправьте ссылку на фото, если требуется или нажмите на 'БЕЗ ФОТО', если фото не требуется",
            reply_markup=admin_send_file_kb()
        )
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(AddProduct.image)
    except ValueError:
        await message.answer(text="Ошибка! Необходимо ввести числовое значение для цены.")
        return


@admin_router.callback_query(F.data == "without_file", F.from_user.id.in_(admins), AddProduct.image)
async def admin_process_without_file(call: CallbackQuery, state: FSMContext):
    await state.update_data(image=None)
    await call.answer('Файл не выбран.')
    msg = await call.message.edit_text(
        text="Введите минимальную упаковку товара:", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.min_packing)


@admin_router.message(F.text, F.from_user.id.in_(admins), AddProduct.image)
async def admin_process_without_file(message: Message, state: FSMContext):
    await state.update_data(image=message.text)
    await process_dell_text_msg(message, state)
    msg = await message.answer(
        text="Введите минимальную упаковку товара:", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.min_packing)


@admin_router.message(F.text, F.from_user.id.in_(admins))
async def admin_process_hidden_content(message: Message, state: FSMContext, session_without_commit: AsyncSession):
    await state.update_data(min_packing=message.text)

    product_data = await state.get_data()
    category_info = await CategoryDao.find_one_or_none_by_id(session=session_without_commit,
                                                             data_id=product_data.get("category_id"))

    image = product_data["image"]

    product_text = (f'🛒 Проверьте, все ли корректно:\n\n'
                    f'🔹 <b>Название товара:</b> {product_data["name"]}\n\n'
                    f'🔹 <b>Описание:</b>\n{product_data["description"]}\n\n'
                    f'🔹 <b>Минимальная упаковка:</b>\n {product_data["min_packing"]}\n\n'
                    f'🔹 <b>Цена:</b> {product_data["price"]} ₽\n\n'
                    f'🔹 <b>Категория:</b> {category_info.category_name} (ID: {category_info.id})')
    await process_dell_text_msg(message, state)

    if image:
        msg = await message.answer_photo(photo=image, caption=product_text, reply_markup=admin_confirm_kb())
    else:
        msg = await message.answer(text=product_text, reply_markup=admin_confirm_kb())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddProduct.confirm_add)


@admin_router.callback_query(F.data == "confirm_add", F.from_user.id.in_(admins))
async def admin_process_confirm_add(call: CallbackQuery, state: FSMContext, session_with_commit: AsyncSession):
    await call.answer('Приступаю к сохранению файла!')
    product_data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=product_data["last_msg_id"])
    del product_data["last_msg_id"]
    await ProductDao.add(session=session_with_commit, values=ProductModel(**product_data))
    await call.message.answer(text="Товар успешно добавлен в базу данных!", reply_markup=admin_kb())

# @admin_router.callback_query(F.data == 'cooking_cheese', F.from_user.id.in_(settings.ADMIN_IDS))
# async def admin_cooking_cheese(call: CallbackQuery, state: FSMContext):
#     await call.answer('Внесение данных по варке сыра')
#     await call.message.delete()
#     msg = await call.message.answer(text="Для начала укажите имя товара: ", reply_markup=cancel_kb_inline())
#     await state.update_data(last_msg_id=msg.message_id)
#     await state.set_state(AddProduct.name)
