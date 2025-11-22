import pytest
from unittest.mock import AsyncMock, MagicMock

from app.crud import add_item_to_order
from app.models import Product, Order, OrderItem
from app.exceptions import NotFoundError, OutOfStockError


@pytest.mark.asyncio
async def test_add_item_success_new_item():
    """Добавление нового товара в заказ"""

    product = Product(id=1, qty=10, price=5)
    order = Order(id=100)

    session = AsyncMock()

    mock_product_result = MagicMock()
    mock_product_result.scalar_one_or_none.return_value = product

    mock_order_result = MagicMock()
    mock_order_result.scalar_one_or_none.return_value = order

    mock_order_item_result = MagicMock()
    mock_order_item_result.scalar_one_or_none.return_value = None

    session.execute.side_effect = [
        mock_product_result,
        mock_order_result,
        mock_order_item_result
    ]

    session.add = AsyncMock()
    session.flush = AsyncMock()

    result, msg = await add_item_to_order(session, 100, 1, 3)

    assert result["order_id"] == 100
    assert result["product_id"] == 1
    assert result["qty"] == 3
    assert result["unit_price"] == 5
    assert result["line_total"] == 15
    assert msg == "Item added/updated"
    assert product.qty == 7
    session.add.assert_called_once()


@pytest.mark.asyncio
async def test_add_item_success_existing_item():
    """Товар уже есть → qty увеличивается"""

    product = Product(id=1, qty=10, price=2)
    order = Order(id=100)
    order_item = OrderItem(order_id=100, product_id=1, qty=5, unit_price=2)

    session = AsyncMock()

    mock_product_result = MagicMock()
    mock_product_result.scalar_one_or_none.return_value = product
    mock_order_result = MagicMock()
    mock_order_result.scalar_one_or_none.return_value = order
    mock_order_item_result = MagicMock()
    mock_order_item_result.scalar_one_or_none.return_value = order_item

    session.execute.side_effect = [
        mock_product_result,
        mock_order_result,
        mock_order_item_result
    ]

    session.add = AsyncMock()
    session.flush = AsyncMock()

    result, msg = await add_item_to_order(session, 100, 1, 2)

    assert result["qty"] == 7
    assert result["line_total"] == 14
    assert product.qty == 8
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_add_item_product_not_found():
    """Товар не найден → NotFoundError"""

    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_result

    with pytest.raises(NotFoundError):
        await add_item_to_order(session, 100, 999, 1)


@pytest.mark.asyncio
async def test_add_item_out_of_stock():
    """Недостаточно товара"""

    product = Product(id=1, qty=1, price=10)
    session = AsyncMock()
    mock_product_result = MagicMock()
    mock_product_result.scalar_one_or_none.return_value = product
    session.execute.return_value = mock_product_result

    with pytest.raises(OutOfStockError):
        await add_item_to_order(session, 100, 1, 5)


@pytest.mark.asyncio
async def test_add_item_order_not_found():
    """Заказ не найден"""

    product = Product(id=1, qty=10, price=5)
    session = AsyncMock()

    mock_product_result = MagicMock()
    mock_product_result.scalar_one_or_none.return_value = product
    mock_order_result = MagicMock()
    mock_order_result.scalar_one_or_none.return_value = None

    session.execute.side_effect = [
        mock_product_result,
        mock_order_result
    ]

    with pytest.raises(NotFoundError):
        await add_item_to_order(session, 100, 1, 1)
