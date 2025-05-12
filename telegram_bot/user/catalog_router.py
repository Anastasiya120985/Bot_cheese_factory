from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from telegram_bot.config import bot, settings
from telegram_bot.dao.dao import CategoryDao, ProductDao, PurchaseDao, CartDao, UserDAO
from telegram_bot.user.kbs import catalog_kb, product_kb, purchases_kb, cart_product_kb, cart_kb
from telegram_bot.user.schemas import ProductCategoryIDModel, PurchaseData, CartData, CartIDUser, TelegramIDModel, CartIDUserProduct, CartQuantity

catalog_router = Router()


@catalog_router.callback_query(F.data == "catalog")
async def page_catalog(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Загрузка каталога...")
    catalog_data = await CategoryDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text="Выберите категорию товаров:",
        reply_markup=catalog_kb(catalog_data)
    )


@catalog_router.callback_query(F.data.startswith("category_"))
async def page_catalog_products(call: CallbackQuery, session_without_commit: AsyncSession):
    category_id = int(call.data.split("_")[-1])
    products_category = await ProductDao.find_all(session=session_without_commit,
                                                  filters=ProductCategoryIDModel(category_id=category_id))
    count_products = len(products_category)
    if count_products:
        await call.answer(f"В данной категории {count_products} товаров.")
        for product in products_category:
            product_text = (
                f"<b>{product.name}</b>\n\n"
                f"📝 {product.description}\n\n"
                f"💰 <b>Цена:</b> {product.price} руб. / {product.min_packing}"
            )
            await call.message.answer_photo(
                photo=product.image,
                caption=product_text,
                reply_markup=product_kb(product.id)
            )
    else:
        await call.answer("В данной категории нет товаров.")


@catalog_router.callback_query(F.data == "product")
async def page_products(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Загрузка товаров...")
    products = await ProductDao.find_all(session=session_without_commit)
    count_products = len(products)
    if count_products:
        await call.answer(f"В наличие {count_products} товаров.")
        for product in products:
            product_text = (
                f"<b>{product.name}</b>\n\n"
                f"📝 {product.description}\n\n"
                f"💰 <b>Цена:</b> {product.price} руб. / {product.min_packing}"
            )
            await call.message.answer_photo(
                photo=product.image,
                caption=product_text,
                reply_markup=product_kb(product.id)
            )
    else:
        await call.answer("В наличие нет товаров.")


@catalog_router.callback_query(F.data.startswith("add_") | F.data.startswith("remove_"))
async def update_cart_handler(call: CallbackQuery, session_without_commit: AsyncSession, session_with_commit: AsyncSession):
    action, product_id = call.data.split("_")
    product_id = int(product_id)
    user = await UserDAO.find_one_or_none(
        session=session_without_commit,
        filters=TelegramIDModel(telegram_id=call.from_user.id)
    )
    user_id = user.id
    carts = await CartDao.find_one_or_none(
        session=session_without_commit,
        filters=CartIDUserProduct(product_id=product_id, user_id=user_id)
    )
    if not carts:
        quantity = 0
    else:
        quantity = carts.quantity
    if action == "add":
        quantity += 1
        cart_data = {
            'user_id': user_id,
            'product_id': product_id,
            'quantity': quantity
        }
        if quantity <= 1:
            # Добавляем товар в корзину
            await CartDao.add(session=session_with_commit, values=CartData(**cart_data))
            await call.answer("✅ Товар добавлен в корзину!")
        else:
            await CartDao.delete(session=session_with_commit, filters=CartIDUserProduct(product_id=product_id, user_id=user_id))
            # Добавляем товар в корзину
            await CartDao.add(session=session_with_commit, values=CartData(**cart_data))
            await call.answer("🔄 Количество товара изменено, обновите Корзину!", show_alert=True)
    elif action == "remove":
        quantity -= 1
        cart_data = {
            'user_id': user_id,
            'product_id': product_id,
            'quantity': quantity
        }
        if quantity < 1:
            await CartDao.delete(session=session_with_commit,
                                 filters=CartIDUserProduct(product_id=product_id, user_id=user_id))
            await call.answer("❌ Товар удален!", show_alert=True)
        else:
            await CartDao.delete(session=session_with_commit,
                                 filters=CartIDUserProduct(product_id=product_id, user_id=user_id))
            await CartDao.add(session=session_with_commit, values=CartData(**cart_data))
            await call.answer("🔄 Количество товара изменено, обновите Корзину!", show_alert=True)


@catalog_router.callback_query(F.data.startswith("cart"))
@catalog_router.callback_query(F.data.startswith("refresh_cart"))
async def cart_command(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Загрузка корзины...")
    user = await UserDAO.find_one_or_none(session=session_without_commit,
                                          filters=TelegramIDModel(telegram_id=call.from_user.id))
    user_id = user.id
    carts = await CartDao.find_all(session=session_without_commit, filters=CartIDUser(user_id=user_id))
    if len(carts) == 0:
        await call.message.answer("Ваша корзина пуста.")
    else:
        await call.message.answer(f"🛒 Ваша корзина:\n")
        total_price = 0
        for cart in carts:
            id_product = cart.product_id
            product = await ProductDao.find_one_or_none_by_id(session=session_without_commit, data_id=id_product)
            price = product.price*cart.quantity
            product_text = (
                f"<b>{product.name}</b>\n"
                f"📝 Количество: {cart.quantity} ({product.min_packing})\n"
                f"💰 <b>Цена:</b> {price} руб. "
            )
            total_price += price
            await call.message.answer(
                text=product_text,
                reply_markup=cart_product_kb(product.id)
            )
        await call.message.answer(
            text=f"<b>Итоговая сумма: {total_price}</b>",
            reply_markup=cart_kb()
        )


@catalog_router.callback_query(F.data.startswith('checkout'))
async def purchase_add(call: CallbackQuery, session_without_commit: AsyncSession, session_with_commit: AsyncSession):
    user = await UserDAO.find_one_or_none(session=session_without_commit,
                                          filters=TelegramIDModel(telegram_id=call.from_user.id))
    user_id = user.id
    carts = await CartDao.find_all(session=session_without_commit, filters=CartIDUser(user_id=user_id))
    text = ''
    total_price = 0
    for cart in carts:
        id_product = int(cart.product_id)
        quantity = int(cart.quantity)
        product = await ProductDao.find_one_or_none_by_id(session=session_without_commit, data_id=id_product)
        price = int(product.price*quantity)
        purchase_data = {
            'user_id': int(user_id),
            'product_id': int(id_product),
            'quantity': int(quantity),
            'price': int(price)
        }
        total_price += price
        text += f"{product.name} - {quantity} шт. × {price}₽ = {quantity * price}₽\n"
        # Добавляем информацию о покупке в базу данных
        await PurchaseDao.add(session=session_with_commit, values=PurchaseData(**purchase_data))
        await CartDao.delete(session=session_with_commit, filters=CartIDUserProduct(product_id=id_product, user_id=user_id))
    text += f"Итоговая сумма - {total_price} ₽"

    # Формируем уведомление администраторам
    for admin_id in settings.ADMIN_IDS:
        try:
            username = call.message.from_user.username
            user_info = f"@{user.username}" if username else f"c ID {user_id}"

            await bot.send_message(
                chat_id=admin_id,
                text=(
                    f"💲 Пользователь {user_info} оформил заказ:\n"
                    f"{text}"
                )
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления администраторам: {e}")

    # Подготавливаем текст для пользователя
    await call.message.answer(f"Ваш заказ оформлен!\n Оплатите {total_price}₽ и отправьте чек в чат", reply_markup=purchases_kb())
