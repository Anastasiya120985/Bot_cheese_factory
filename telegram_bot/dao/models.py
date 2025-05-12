from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, String
from telegram_bot.dao.database import Base


class User(Base):
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    purchases: Mapped[List['Purchase']] = relationship(
        "Purchase",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    carts: Mapped[List['Cart']] = relationship(
        "Cart",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"


class Category(Base):
    __tablename__ = 'categories'

    category_name: Mapped[str] = mapped_column(Text, nullable=False)
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.category_name}')>"


class Product(Base):
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    min_packing: Mapped[str] = mapped_column(Text)
    price: Mapped[int]
    image: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    purchases: Mapped[List['Purchase']] = relationship(
        "Purchase",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    carts: Mapped[List['Cart']] = relationship(
        "Cart",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"


class Cart(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped["User"] = relationship("User", back_populates="carts")
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped["Product"] = relationship("Product", back_populates="carts")
    quantity: Mapped[int]

    def __repr__(self):
        return f"<Purchase(id={self.id}, user_id={self.user_id}, product_id={self.product_id}, date={self.created_at})>"


class Purchase(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped["User"] = relationship("User", back_populates="purchases")
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    product: Mapped['Product'] = relationship("Product", back_populates="purchases")
    quantity: Mapped[int]
    price: Mapped[int]

    def __repr__(self):
        return f"<Purchase(id={self.id}, user_id={self.user_id}, product_id={self.product_id}, date={self.created_at})>"


#
# class Milk(Base):
#     name_milk: Mapped[str]
#
#     def __repr__(self):
#         return f"<Milk(id={self.id}, name='{self.name_milk}')>"
#
#
# class Coagulant(Base):
#     name_coagulant: Mapped[str]
#
#     def __repr__(self):
#         return f"<Coagulant(id={self.id}, name='{self.name_coagulant}')>"
#
#
# class Pickle(Base):
#     name_pickle: Mapped[str]
#
#     def __repr__(self):
#         return f"<Pickle(id={self.id}, name='{self.name_pickle}')>"