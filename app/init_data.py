# app/db/init_data.py
import asyncio
from datetime import datetime, timedelta

from app.database import async_session
from app.models import Client, Category, Product, Order, OrderItem

# Запуск планируется вне FastAPI,
# поэтому использую асинхронную сессию саму по себе без get_session генератора описанного в database
async def init_data():
    async with async_session() as session:
        # Очистка таблиц (на случай повторного запуска)
        for model in [OrderItem, Order, Product, Category, Client]:
            await session.execute(f"DELETE FROM {model.__tablename__};")

        # Клиенты
        clients = [
            Client(id=1, name="Client A", address="Main Street 1"),
            Client(id=2, name="Client B", address="Second Avenue 22"),
            Client(id=3, name="Client C", address="Industrial Road 9"),
        ]
        session.add_all(clients)

        # Категории с вложенностью
        categories = [
            Category(id=1, name="Electronics", parent_id=None),
            Category(id=2, name="Smartphones", parent_id=1),
            Category(id=3, name="Laptops", parent_id=1),
            Category(id=4, name="Appliances", parent_id=None),
            Category(id=5, name="Kitchen", parent_id=4),
        ]
        session.add_all(categories)

        # Товары
        products = [
            Product(id=1, name="iPhone 15", category_id=2, qty=20, price=999.99, root_category_id=1),
            Product(id=2, name="MacBook Air", category_id=3, qty=15, price=1299.99, root_category_id=1),
            Product(id=3, name="Samsung Galaxy S24", category_id=2, qty=25, price=899.99, root_category_id=1),
            Product(id=4, name="Blender Pro 3000", category_id=5, qty=30, price=199.99, root_category_id=4),
            Product(id=5, name="Microwave X10", category_id=5, qty=10, price=249.99, root_category_id=4),
            Product(id=6, name="Gaming Laptop Nitro 5", category_id=3, qty=8, price=1499.99, root_category_id=1),
        ]
        session.add_all(products)

        await session.flush()  # чтобы гарантировать наличие ID

        now = datetime.utcnow()
        last_month = now - timedelta(days=30)

        # Заказы
        orders = [
            Order(id=1, client_id=1, created_at=last_month + timedelta(days=5)),
            Order(id=2, client_id=1, created_at=now - timedelta(days=10)),
            Order(id=3, client_id=2, created_at=now - timedelta(days=3)),
            Order(id=4, client_id=3, created_at=now - timedelta(days=25)),
        ]
        session.add_all(orders)

        await session.flush()

        # Позиции заказов
        order_items = [
            OrderItem(order_id=1, product_id=1, qty=2, unit_price=999.99),
            OrderItem(order_id=1, product_id=2, qty=1, unit_price=1299.99),
            OrderItem(order_id=2, product_id=1, qty=3, unit_price=999.99),
            OrderItem(order_id=2, product_id=4, qty=2, unit_price=199.99),
            OrderItem(order_id=3, product_id=3, qty=5, unit_price=899.99),
            OrderItem(order_id=3, product_id=5, qty=1, unit_price=249.99),
            OrderItem(order_id=4, product_id=6, qty=1, unit_price=1499.99),
            OrderItem(order_id=4, product_id=2, qty=1, unit_price=1299.99),
        ]
        session.add_all(order_items)

        await session.commit()
        print("✅ Тестовые данные успешно добавлены!")


if __name__ == "__main__":
    asyncio.run(init_data())
