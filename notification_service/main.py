from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Notification Service")

class NotificationRequest(BaseModel):
    user_id: int
    message: str

@app.post("/send")
async def send_notification(notif: NotificationRequest):
    # In a real app, this would send an email, push notification, etc.
    print(f"NOTIFICATION FOR USER {notif.user_id}: {notif.message}")
    return {"status": "sent"}
