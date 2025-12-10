from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import datetime

app = FastAPI(title="Review Service")

class Review(BaseModel):
    product_id: int
    comment: str
    rating: int | None = None  # optional 1-5
    username: str | None = None  # optional username

# In-memory storage for reviews
reviews: Dict[int, List[Dict]] = {
    1: [
        {"id": 1, "product_id": 1, "rating": 5, "comment": "Amazing laptop, very fast!", "username": "user", "date": "2025-12-01"},
        {"id": 2, "product_id": 1, "rating": 4, "comment": "Good value for the price.", "username": "another_user", "date": "2025-12-02"},
    ]
}

@app.get("/reviews/{product_id}", response_model=List[Dict])
async def get_reviews_for_product(product_id: int):
    return reviews.get(product_id, [])

@app.post("/reviews")
async def submit_review(review: Review):
    product_id = review.product_id
    if product_id not in reviews:
        reviews[product_id] = []
    
    new_review_id = len(reviews[product_id]) + 1
    # Apply sensible defaults for optional fields
    new_review = review.dict()
    if not new_review.get("username"):
        new_review["username"] = "anonymous"
    if not new_review.get("rating"):
        new_review["rating"] = 5
    new_review["id"] = new_review_id
    new_review["date"] = datetime.date.today().isoformat()
    
    reviews[product_id].append(new_review)
    
    return new_review
