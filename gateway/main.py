import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs from environment variables or defaults
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8002")
CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://cart_service:8003")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order_service:8004")
REVIEW_SERVICE_URL = os.getenv("REVIEW_SERVICE_URL", "http://review_service:8007")


async def proxy_request(url: str, method: str, request: Request):
    async with httpx.AsyncClient() as client:
        try:
            headers = {key: value for key, value in request.headers.items() if key.lower() not in ['host', 'content-length']}
            
            data = await request.body()
            
            resp = await client.request(method, url, content=data, headers=headers)
            
            # Try to parse as JSON, fallback to text if it fails
            try:
                content = resp.json()
            except:
                content = {"detail": resp.text}
            
            response_headers = {key: value for key, value in resp.headers.items() if key.lower() not in ['content-encoding', 'transfer-encoding']}
            
            return JSONResponse(content=content, status_code=resp.status_code, headers=response_headers)

        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {e.request.url}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# --- Auth Routes ---
@app.api_route("/auth/{path:path}", methods=["POST"], operation_id="auth_service_proxy")
async def auth_proxy(path: str, request: Request):
    return await proxy_request(f"{AUTH_SERVICE_URL}/{path}", request.method, request)

# --- Product Routes ---
@app.api_route("/products/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], operation_id="products_proxy_with_path")
@app.api_route("/products", methods=["GET", "POST"], operation_id="products_proxy_root")
async def products_proxy(request: Request, path: str = ""):
    url = f"{PRODUCT_SERVICE_URL}/products"
    if path:
        url += f"/{path}"
    return await proxy_request(url, request.method, request)

# --- Cart Routes ---
@app.api_route("/cart/{path:path}", methods=["GET", "POST", "DELETE"], operation_id="cart_service_proxy")
async def cart_proxy(path: str, request: Request):
    return await proxy_request(f"{CART_SERVICE_URL}/cart/{path}", request.method, request)

# --- Order Routes ---
@app.post("/orders", operation_id="create_order")
async def orders_proxy_post(request: Request):
    return await proxy_request(f"{ORDER_SERVICE_URL}/orders", request.method, request)

@app.api_route("/orders/{path:path}", methods=["GET"], operation_id="get_orders")
async def orders_proxy_get(path: str, request: Request):
    return await proxy_request(f"{ORDER_SERVICE_URL}/orders/{path}", request.method, request)

# --- Review Routes ---
@app.api_route("/reviews/{path:path}", methods=["GET", "POST"], operation_id="reviews_proxy_with_path")
async def reviews_proxy(path: str, request: Request):
    return await proxy_request(f"{REVIEW_SERVICE_URL}/reviews/{path}", request.method, request)

@app.api_route("/reviews", methods=["POST"], operation_id="create_review")
async def reviews_root_post(request: Request):
    return await proxy_request(f"{REVIEW_SERVICE_URL}/reviews", request.method, request)

@app.get("/")
async def root():
    return {"message": "Welcome to the API Gateway"}
