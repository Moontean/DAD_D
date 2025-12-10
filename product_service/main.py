from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Product Service")

class Product(BaseModel):
    name: str
    price: float

products_db = [
    {"id": 1, "name": "Gaming Laptop ASUS ROG", "price": 1499.99, "description": "High-performance gaming laptop with RTX 4070, 16GB RAM, perfect for gaming and content creation."},
    {"id": 2, "name": "iPhone 15 Pro Max", "price": 1199.99, "description": "Latest iPhone with titanium design, A17 Pro chip, and professional camera system."},
    {"id": 3, "name": "Sony WH-1000XM5 Headphones", "price": 399.99, "description": "Industry-leading noise canceling wireless headphones with 30-hour battery life."},
    {"id": 4, "name": "Mechanical Keyboard Corsair K95", "price": 179.99, "description": "Premium mechanical gaming keyboard with RGB backlighting and programmable keys."},
    {"id": 5, "name": "Logitech MX Master 3S Mouse", "price": 99.99, "description": "Advanced wireless mouse designed for productivity with precision scrolling."},
    {"id": 6, "name": "Samsung 27\" 4K Monitor", "price": 329.99, "description": "Ultra HD 4K monitor with vibrant colors and wide viewing angles for work and entertainment."},
    {"id": 7, "name": "iPad Pro 12.9\"", "price": 1099.99, "description": "Powerful tablet with M2 chip, perfect for creative professionals and digital artists."},
    {"id": 8, "name": "AirPods Pro (2nd Gen)", "price": 249.99, "description": "Premium wireless earbuds with active noise cancellation and spatial audio."},
    {"id": 9, "name": "Nintendo Switch OLED", "price": 349.99, "description": "Portable gaming console with vibrant OLED screen and exclusive Nintendo games."},
    {"id": 10, "name": "MacBook Air M2", "price": 1199.99, "description": "Ultra-thin laptop with Apple M2 chip, all-day battery life, and stunning Retina display."},
]

@app.get("/products", response_model=List[dict])
async def list_products():
    return products_db

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    for p in products_db:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/products", status_code=201)
async def create_product(product: Product):
    new_id = max(p["id"] for p in products_db) + 1 if products_db else 1
    new_product = {"id": new_id, "name": product.name, "price": product.price}
    products_db.append(new_product)
    return new_product

@app.put("/products/{product_id}")
async def update_product(product_id: int, product: Product):
    for i, p in enumerate(products_db):
        if p["id"] == product_id:
            products_db[i]["name"] = product.name
            products_db[i]["price"] = product.price
            return products_db[i]
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    for i, p in enumerate(products_db):
        if p["id"] == product_id:
            del products_db[i]
            return {"message": "Product deleted"}
    raise HTTPException(status_code=404, detail="Product not found")
