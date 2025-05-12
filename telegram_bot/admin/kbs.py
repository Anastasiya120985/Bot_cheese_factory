from typing import List
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from telegram_bot.dao.models import Category


def catalog_admin_kb(catalog_data: List[Category]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in catalog_data:
        kb.button(text=category.category_name, callback_data=f"add_category_{category.id}")
    kb.button(text="Отмена", callback_data="admin_panel")
    kb.adjust(2)
    return kb.as_markup()


def admin_send_file_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Без фото", callback_data="without_file")
    kb.button(text="Отмена", callback_data="admin_panel")
    kb.adjust(2)
    return kb.as_markup()


def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Статистика", callback_data="statistic")
    kb.button(text="🛍️ Управлять товарами", callback_data="process_products")
    # kb.button(text="🧀 Варка сыра", callback_data="cooking_cheese")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2)
    return kb.as_markup()


def admin_kb_back() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def dell_change_product_kb(product_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑️ Удалить", callback_data=f"dell_{product_id}")
    kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1, 2)
    return kb.as_markup()


def change_product_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Наименование", callback_data="name")
    kb.button(text="Описание", callback_data="description")
    kb.button(text="Категория", callback_data="category")
    kb.button(text="Фото", callback_data="image")
    kb.button(text="Цена", callback_data="price")
    kb.button(text="Минимальная упаковка", callback_data="min_packing")
    kb.adjust(2, 2, 2)
    return kb.as_markup()


def product_management_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить товар", callback_data="add_product")
    kb.button(text="🗑️ Удалить товар", callback_data="delete_product")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def cancel_kb_inline() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="cancel")
    return kb.as_markup()


def admin_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Все верно", callback_data="confirm_add")
    kb.button(text="Отмена", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()


# def date_cooking_cheese_kb() -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="Сегодня", callback_data="today_date_cooking")
#     kb.button(text="Вчера", callback_data="yesterday_date_cooking")
#     kb.button(text="Другая дата", callback_data="other_date_cooking")
#     kb.adjust(2, 1)
#     return kb.as_markup()
#
#
# def choice_milk_kb() -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     kb.button(text="Смешанное", callback_data="mixed_milk")
#     kb.adjust(1)
#     return kb.as_markup()