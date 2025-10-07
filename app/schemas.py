from pydantic import BaseModel, conint

class AddItemRequest(BaseModel):
    order_id: int
    product_id: int
    qty: conint(gt=0)

class AddItemResponse(BaseModel):
    order_id: int
    product_id: int
    qty: int
    unit_price: float
    line_total: float
    message: str