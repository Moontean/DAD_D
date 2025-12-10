from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Auth Service")

# In-memory user store
users_db = {
    "user": {"username": "user", "password": "password", "role": "user", "id": 1},
    "admin": {"username": "admin", "password": "admin", "role": "admin", "id": 2}
}

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

@app.post("/register")
async def register(creds: RegisterRequest):
    if creds.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_id = len(users_db) + 1
    users_db[creds.username] = {
        "username": creds.username,
        "password": creds.password, # In a real app, hash this!
        "role": "user",
        "id": new_id
    }
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(creds: LoginRequest):
    user = users_db.get(creds.username)
    if user and user["password"] == creds.password:
        return {
            "token": f"fake-jwt-token-{user['id']}", 
            "user_id": user['id'],
            "role": user['role'],
            "username": user['username']
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")
