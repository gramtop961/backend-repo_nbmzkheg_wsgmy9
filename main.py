import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import Event, GalleryImage, ContactMessage, CenterInfo, WeeklyHour

app = FastAPI(title="Ješenca-Požeg Community Center API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Ješenca-Požeg Community Center API"}


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

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Static info for the center (can be later moved to DB if needed)
_DEFAULT_INFO = CenterInfo(
    name="Ješenca-Požeg Community Center",
    address="Ješenca 1",
    city="Požeg",
    country="Slovenia",
    latitude=46.2711,
    longitude=15.3793,
    email="info@jesenca-pozeg.si",
    phone="+386 41 123 456",
    website=None,
    schedule=[
        WeeklyHour(day="Monday", open="09:00", close="17:00"),
        WeeklyHour(day="Tuesday", open="09:00", close="17:00"),
        WeeklyHour(day="Wednesday", open="09:00", close="17:00"),
        WeeklyHour(day="Thursday", open="09:00", close="17:00"),
        WeeklyHour(day="Friday", open="09:00", close="17:00"),
        WeeklyHour(day="Saturday", open="10:00", close="14:00", note="Events only"),
        WeeklyHour(day="Sunday", open="Closed", close="Closed", note="Closed")
    ]
)


@app.get("/api/info", response_model=CenterInfo)
async def get_center_info():
    return _DEFAULT_INFO


# Events Endpoints
@app.post("/api/events", status_code=201)
async def create_event(event: Event):
    # Ensure times are proper ISO strings for storage
    data = event.model_dump()
    inserted_id = create_document("event", data)
    return {"id": inserted_id, "message": "Event created"}


@app.get("/api/events")
async def list_events(limit: Optional[int] = 100):
    events = get_documents("event", {}, limit)
    # Convert ObjectId to string if present
    for e in events:
        if "_id" in e:
            e["id"] = str(e.pop("_id"))
    # Sort by start date ascending
    try:
        events.sort(key=lambda x: x.get("start"))
    except Exception:
        pass
    return events


# Gallery Endpoints
@app.post("/api/gallery", status_code=201)
async def add_image(image: GalleryImage):
    inserted_id = create_document("galleryimage", image)
    return {"id": inserted_id, "message": "Image added"}


@app.get("/api/gallery")
async def get_gallery(limit: Optional[int] = 50):
    images = get_documents("galleryimage", {}, limit)
    for img in images:
        if "_id" in img:
            img["id"] = str(img.pop("_id"))
    return images


# Contact Endpoint
@app.post("/api/contact", status_code=201)
async def send_message(msg: ContactMessage):
    inserted_id = create_document("contactmessage", msg)
    return {"id": inserted_id, "message": "Message received"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
