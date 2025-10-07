from sqlalchemy import Column, Integer, BigInteger, String, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship, mapped_column
from .database import Base

class Category(Base):
    __tablename__ = "category"
    id = mapped_column(BigInteger, primary_key=True)
    name = mapped_column(String, nullable=False)
    parent_id = mapped_column(BigInteger, ForeignKey("category.id"), nullable=True)

class CategoryClosure(Base):
    __tablename__ = "category_closure"
    ancestor_id = mapped_column(BigInteger, ForeignKey("category.id"), primary_key=True)
    descendant_id = mapped_column(BigInteger, ForeignKey("category.id"), primary_key=True)
    depth = mapped_column(Integer, nullable=False)

class Product(Base):
    __tablename__ = "product"
    id = mapped_column(BigInteger, primary_key=True)
    name = mapped_column(String, nullable=False)
    category_id = mapped_column(BigInteger, ForeignKey("category.id"), nullable=False)
    qty = mapped_column(BigInteger, nullable=False, default=0)
    price = mapped_column(Numeric(12,2), nullable=False)
    root_category_id = mapped_column(BigInteger, nullable=True)

class Client(Base):
    __tablename__ = "client"
    id = mapped_column(BigInteger, primary_key=True)
    name = mapped_column(String, nullable=False)
    address = mapped_column(String, nullable=True)

class Order(Base):
    __tablename__ = "orders"
    id = mapped_column(BigInteger, primary_key=True)
    client_id = mapped_column(BigInteger, ForeignKey("client.id"), nullable=False)

class OrderItem(Base):
    __tablename__ = "order_item"
    order_id = mapped_column(BigInteger, ForeignKey("orders.id"), primary_key=True)
    product_id = mapped_column(BigInteger, ForeignKey("product.id"), primary_key=True)
    qty = mapped_column(BigInteger, nullable=False)
    unit_price = mapped_column(Numeric(12,2), nullable=False)