from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ─── Models ──────────────────────────────────────────────────────────

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class ShowcaseItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mobile_image: str
    laptop_image: str
    order: int = 0

class Feature(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    icon: str
    title: str
    description: str
    mockup_type: str
    order: int = 0

class Stats(BaseModel):
    model_config = ConfigDict(extra="ignore")
    users_count: str = "3M+"
    description: str = "users worldwide building & launching real applications in minutes."

class WaitlistEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WaitlistCreate(BaseModel):
    email: str
    name: Optional[str] = None


# ─── Seed Data ───────────────────────────────────────────────────────

SEED_SHOWCASE = [
    {
        "mobile_image": "https://assets.emergent.sh/assets/showcase/Mob1.webp",
        "laptop_image": "https://assets.emergent.sh/assets/showcase/Laptop1.webp",
        "order": 1
    },
    {
        "mobile_image": "https://assets.emergent.sh/assets/showcase/Mob2.webp",
        "laptop_image": "https://assets.emergent.sh/assets/showcase/Laptop2.webp",
        "order": 2
    },
    {
        "mobile_image": "https://assets.emergent.sh/assets/showcase/Mob3.webp",
        "laptop_image": "https://assets.emergent.sh/assets/showcase/Laptop3.webp",
        "order": 3
    },
    {
        "mobile_image": "https://assets.emergent.sh/assets/showcase/Mob4.webp",
        "laptop_image": "https://assets.emergent.sh/assets/showcase/Laptop4.webp",
        "order": 4
    },
]

SEED_FEATURES = [
    {
        "icon": "monitor-smartphone",
        "title": "Build websites and mobile apps",
        "description": "Transform your ideas into fully functional websites and mobile apps with instant deployment, seamless data connections, and powerful scalability.",
        "mockup_type": "library",
        "order": 1
    },
    {
        "icon": "bot",
        "title": "Build custom agents",
        "description": "Create intelligent AI agents that automate tasks, answer questions, and interact with your users. Deploy them anywhere with just a few clicks.",
        "mockup_type": "agent",
        "order": 2
    },
    {
        "icon": "link",
        "title": "Build powerful integrations",
        "description": "Connect your apps to thousands of services and APIs. Build complex workflows with ease using our integration framework.",
        "mockup_type": "integration",
        "order": 3
    },
]

SEED_STATS = {
    "users_count": "3M+",
    "description": "users worldwide building & launching real applications in minutes."
}


# ─── Routes ──────────────────────────────────────────────────────────

@api_router.get("/")
async def root():
    return {"message": "maligeeAi API is running"}


# --- Showcase ---
@api_router.get("/showcase", response_model=List[ShowcaseItem])
async def get_showcase():
    items = await db.showcase.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    if not items:
        # Auto-seed if empty
        await seed_data_internal()
        items = await db.showcase.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return items


# --- Features ---
@api_router.get("/features", response_model=List[Feature])
async def get_features():
    items = await db.features.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    if not items:
        await seed_data_internal()
        items = await db.features.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return items


# --- Stats ---
@api_router.get("/stats", response_model=Stats)
async def get_stats():
    stats = await db.stats.find_one({}, {"_id": 0})
    if not stats:
        await seed_data_internal()
        stats = await db.stats.find_one({}, {"_id": 0})
    return stats or Stats()


# --- Waitlist ---
@api_router.post("/waitlist", response_model=WaitlistEntry)
async def create_waitlist_entry(entry: WaitlistCreate):
    # Check for duplicate email
    existing = await db.waitlist.find_one({"email": entry.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already on waitlist")

    waitlist_obj = WaitlistEntry(**entry.model_dump())
    doc = waitlist_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.waitlist.insert_one(doc)
    logger.info(f"New waitlist entry: {entry.email}")
    return waitlist_obj


@api_router.get("/waitlist/count")
async def get_waitlist_count():
    count = await db.waitlist.count_documents({})
    return {"count": count}


# --- Seed ---
async def seed_data_internal():
    """Seed the database with initial data if collections are empty."""
    # Showcase
    if await db.showcase.count_documents({}) == 0:
        for item_data in SEED_SHOWCASE:
            item = ShowcaseItem(**item_data)
            await db.showcase.insert_one(item.model_dump())
        logger.info("Seeded showcase collection")

    # Features
    if await db.features.count_documents({}) == 0:
        for item_data in SEED_FEATURES:
            item = Feature(**item_data)
            await db.features.insert_one(item.model_dump())
        logger.info("Seeded features collection")

    # Stats
    if await db.stats.count_documents({}) == 0:
        await db.stats.insert_one(SEED_STATS)
        logger.info("Seeded stats collection")


@api_router.post("/seed")
async def seed_data():
    """Manually trigger database seeding."""
    await seed_data_internal()
    return {"message": "Database seeded successfully"}


# --- Status (original) ---
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()