# app/crud.py
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Product, Order, OrderItem
from app.exceptions import NotFoundError, OutOfStockError


async def add_item_to_order(session: AsyncSession, order_id: int, product_id: int, qty: int):
    # Получаем товар
    result = await session.execute(select(Product).where(Product.id == product_id).with_for_update())
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundError("Product not found")

    if product.qty < qty:
        raise OutOfStockError("Not enough product in stock")

    # Проверяем заказ
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise NotFoundError("Order not found")

    # Проверяем, есть ли уже такой элемент в заказе
    result = await session.execute(
        select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.product_id == product_id).with_for_update()
    )
    oi = result.scalar_one_or_none()

    if oi:
        oi.qty += qty
        await session.flush()
    else:
        oi = OrderItem(
            order_id=order_id,
            product_id=product_id,
            qty=qty,
            unit_price=product.price
        )
        session.add(oi)
        await session.flush()

    # Уменьшаем остаток
    product.qty -= qty

    # Возвращаем словарь с нужными полями
    return {
        "order_id": order_id,
        "product_id": product.id,
        "qty": oi.qty,
        "unit_price": float(product.price),
        "line_total": float(product.price * oi.qty)
    }, "Item added/updated"

# async def add_item_to_order(session: AsyncSession, order_id: int, product_id: int, qty: int):
#     """
#     Ожидает, что вызывающий код откроет транзакцию (session.begin()).
#     Возвращает словарь с данными добавленной/обновлённой позиции.
#     Бросает NotFoundError / OutOfStockError.
#     """
#     # 1) Блокируем строку продукта
#     res = await session.execute(
#         select(Product).where(Product.id == product_id).with_for_update()
#     )
#     product = res.scalars().first()
#     if product is None:
#         raise NotFoundError("Product not found")
#
#     if product.qty < qty:
#         raise OutOfStockError("Not enough product in stock")
#
#     # 2) Проверяем что заказ существует
#     res = await session.execute(select(Order).where(Order.id == order_id))
#     order = res.scalars().first()
#     if order is None:
#         raise NotFoundError("Order not found")
#
#     # 3) Блокируем/получаем существующую позицию
#     res = await session.execute(
#         select(OrderItem).where(
#             OrderItem.order_id == order_id,
#             OrderItem.product_id == product_id
#         ).with_for_update()
#     )
#     oi = res.scalars().first()
#
#     if oi:
#         oi.qty = oi.qty + qty
#         await session.flush()
#         item_id = oi.id
#         new_qty = oi.qty
#     else:
#         oi = OrderItem(
#             order_id=order_id,
#             product_id=product_id,
#             qty=qty,
#             unit_price=product.price
#         )
#         session.add(oi)
#         await session.flush()  # получим oi.id после flush
#         item_id = oi.id
#         new_qty = oi.qty
#
#     # 4) Резервируем/уменьшаем склад
#     product.qty = product.qty - qty
#     await session.flush()
#
#     return {
#         "item_id": item_id,
#         "order_id": order_id,
#         "product_id": product_id,
#         "qty": new_qty,
#         "unit_price": float(product.price),
#         "line_total": float(product.price * new_qty),
#         "message": "Item added/updated"
#     }
