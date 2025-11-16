import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import User, Product, Order, Enrollment, Testimonial, MediaItem, CommunityEvent, ContactMessage

app = FastAPI(title="Bilal Qori – Trainer Soulful Qur’an API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Bilal Qori API running"}


# Schema explorer for admin tooling
@app.get("/schema")
def get_schema():
    return {
        "collections": [
            "user", "product", "order", "enrollment",
            "testimonial", "mediaitem", "communityevent", "contactmessage"
        ]
    }


# Products: list & seed defaults if empty
@app.get("/products")
def list_products():
    try:
        items = get_documents("product", {}, limit=200)
        if not items:
            # Seed a few showcase products
            defaults: List[Product] = [
                Product(title="Murottal Bilal Qori – Vol.1", description="Audio premium 320kbps", price=9.99, category="audio", image="/media/murottal1.jpg"),
                Product(title="E-book Soulful Qur’an Basics", description="Panduan maqomat & rasa", price=14.9, category="ebook", image="/media/ebook-sq.jpg"),
                Product(title="Kaos Soulful Qur’an", description="Cotton combed 24s", price=12.0, category="merchandise", image="/media/tee-sq.jpg")
            ]
            for p in defaults:
                create_document("product", p)
            items = get_documents("product", {}, limit=200)
        # Convert ObjectId to str where needed
        for it in items:
            if "_id" in it:
                it["id"] = str(it.pop("_id"))
        return {"data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CheckoutRequest(BaseModel):
    items: List[dict]
    customer_email: Optional[str] = None
    provider: str = "stripe"  # stripe | razorpay (placeholder)


@app.post("/checkout")
def create_checkout_session(payload: CheckoutRequest):
    # For demo: store order, return a mock checkout URL
    try:
        total = 0.0
        order_items = []
        for it in payload.items:
            qty = int(it.get("qty", 1))
            price = float(it.get("price", 0))
            total += qty * price
            order_items.append({
                "product_id": str(it.get("id", "")),
                "title": it.get("title", "Product"),
                "qty": qty,
                "price": price,
            })
        order = Order(user_email=payload.customer_email or "guest@example.com", items=order_items, total=round(total, 2))
        order_id = create_document("order", order)
        return {
            "checkout_url": f"/pay/mock/{order_id}",
            "order_id": order_id,
            "provider": payload.provider,
            "note": "Demo checkout created. Integrate Stripe/Razorpay by replacing this endpoint."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/journey")
def journey():
    benefits = [
        "Meningkatkan penghayatan dan makna tilawah",
        "Menguasai maqomat dengan pendekatan rasa",
        "Latihan suara dan pernafasan yang aman",
        "Pembelajaran digital yang relevan dan hangat",
    ]
    testimonials = get_documents("testimonial", {}, limit=20) if db else []
    for t in testimonials:
        if "_id" in t:
            t["id"] = str(t.pop("_id"))
    return {"benefits": benefits, "testimonials": testimonials}


@app.post("/enroll")
def enroll(data: Enrollment):
    try:
        _id = create_document("enrollment", data)
        return {"status": "ok", "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/contact")
def contact(msg: ContactMessage):
    try:
        _id = create_document("contactmessage", msg)
        return {"status": "ok", "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/media")
def media_list():
    try:
        items = get_documents("mediaitem", {}, limit=50)
        for it in items:
            if "_id" in it:
                it["id"] = str(it.pop("_id"))
        return {"data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/community")
def community():
    try:
        events = get_documents("communityevent", {}, limit=20)
        for e in events:
            if "_id" in e:
                e["id"] = str(e.pop("_id"))
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
