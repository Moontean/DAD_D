import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="Order Service")

PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment_service:8005")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification_service:8006")

class OrderRequest(BaseModel):
    user_id: int
    items: list
    total_amount: float

class StoredOrder(BaseModel):
    order_id: str
    user_id: int
    items: list
    total_amount: float
    status: str

# In-memory store: {user_id: [orders]}
orders_db = {}

@app.post("/orders")
async def create_order(order: OrderRequest):
    # 1. Process Payment
    try:
        async with httpx.AsyncClient() as client:
            payment_resp = await client.post(
                f"{PAYMENT_SERVICE_URL}/pay",
                json={
                    "amount": order.total_amount,
                    "user_id": str(order.user_id)
                }
            )
            payment_resp.raise_for_status()
            
            # 2. Send Notification
            await client.post(f"{NOTIFICATION_SERVICE_URL}/send", json={"user_id": order.user_id, "message": f"Order placed successfully! Total: ${order.total_amount}"})

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {e.request.url}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Downstream service error: {e.response.text}")

    new_order = {
        "order_id": "some-random-id",
        "user_id": order.user_id,
        "items": order.items,
        "total_amount": order.total_amount,
        "status": "confirmed"
    }
    orders_db.setdefault(order.user_id, []).append(new_order)
    return new_order

@app.get("/orders/{user_id}")
async def list_orders(user_id: int):
    return orders_db.get(user_id, [])
