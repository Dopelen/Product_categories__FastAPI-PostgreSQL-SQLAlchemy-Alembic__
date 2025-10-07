from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import AddItemRequest, AddItemResponse
from app.database import get_session  # dependency that yields AsyncSession
from app.crud import add_item_to_order
from app.exceptions import NotFoundError, OutOfStockError

app = FastAPI(title="Product categories API")

@app.post("/orders/add-item", response_model=AddItemResponse)
async def add_item(req: AddItemRequest, session: AsyncSession = Depends(get_session)):
    try:
        async with session.begin():
            result, message = await add_item_to_order(session, req.order_id, req.product_id, req.qty)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OutOfStockError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error")

    return AddItemResponse(
        order_id=result["order_id"],
        product_id=result["product_id"],
        qty=result["qty"],
        unit_price=result["unit_price"],
        line_total=result["line_total"],
        message=message,
    )
