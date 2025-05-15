from typing import List
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telegram_bot.config import settings
from telegram_bot.dao.models import Category


def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🧀 В наличии", callback_data="product")
    kb.button(text="🛍 По категориям", callback_data="catalog")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.button(text="ℹ️ О нас", callback_data="about")
    if user_id in settings.ADMIN_IDS:
        kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def catalog_kb(catalog_data: List[Category]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in catalog_data:
        kb.button(text=category.category_name, callback_data=f"category_{category.id}")
    kb.button(text="🏠 На Главную", callback_data="home")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.adjust(2, 1, 1, 1, 2, 2)
    return kb.as_markup()


def product_kb(product_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💸 Добавить в Корзину", callback_data=f"add_cart_{product_id}")
    kb.button(text="🏠 На Главную", callback_data="home")
    kb.button(text="🛒 Корзина", callback_data="cart")
    kb.adjust(1, 2)
    return kb.as_markup()


def cart_product_kb(product_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕", callback_data=f"add_cart_{product_id}")
    kb.button(text="➖", callback_data=f"remove_cart_{product_id}")
    kb.adjust(2)
    return kb.as_markup()


def cart_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Обновить корзину", callback_data="refresh_cart")
    kb.button(text="✅ Оформить заказ", callback_data="checkout")
    kb.button(text="🏠 На Главную", callback_data="home")
    kb.adjust(2, 1)
    return kb.as_markup()


def purchases_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Оплатить", url='https://www.tinkoff.ru/rm/r_WEzSibSuRo.QwicRfVdHT/lyOJJ57814')
    kb.adjust(1)
    return kb.as_markup()
