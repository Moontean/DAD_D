from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Cart Service")

# In-memory storage: {user_id: [items]}
carts: Dict[int, List[dict]] = {}
# Model for cart item
class CartItem(BaseModel):
    product_id: int
    quantity: int

@app.get("/cart/{user_id}")
async def get_cart(user_id: int):
    return carts.get(user_id, [])

@app.post("/cart/{user_id}/add")
async def add_to_cart(user_id: int, item: CartItem):
    if user_id not in carts:
        carts[user_id] = []
    
    # Check if item exists and update quantity
    for cart_item in carts[user_id]:
        if cart_item["product_id"] == item.product_id:
            cart_item["quantity"] += item.quantity
            return {"message": "Item quantity updated", "cart": carts[user_id]}

    carts[user_id].append(item.dict())
    return {"message": "Item added", "cart": carts[user_id]}

@app.delete("/cart/{user_id}/clear")
async def clear_cart(user_id: int):
    if user_id in carts:
        carts[user_id] = []
    return {"message": "Cart cleared"}
