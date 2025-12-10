from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Payment Service")

class PaymentRequest(BaseModel):
    amount: float

class PaymentRequest(BaseModel):
    amount: float
    user_id: str


@app.post("/pay")
async def process_payment(payment: PaymentRequest):
    # Basic validation
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    # Always succeed in development to avoid blocking checkout
    return {"status": "success", "transaction_id": f"txn_{payment.user_id}_{int(payment.amount*100)}"}
    
    return {"status": "success", "transaction_id": f"tx_{random.randint(10000, 99999)}"}
