from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ.get('JWT_SECRET', 'maligeeai-secret-key-change-in-prod-2025')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_HOURS = 72
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer(auto_error=False)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: Optional[str] = None
    created_at: str
    build_count: int = 0
    has_free_build: bool = True

class BuildCreate(BaseModel):
    name: str
    description: Optional[str] = None

class BuildResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    status: str
    is_free: bool
    payment_status: str
    created_at: str
    updated_at: str

class BuildEdit(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

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


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(credentials.credentials)
    user = await db.users.find_one({"id": payload['user_id']}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        user = await db.users.find_one({"id": payload['user_id']}, {"_id": 0})
        return user
    except Exception:
        return None


@api_router.post("/auth/signup")
async def signup(data: UserCreate):
    existing = await db.users.find_one({"email": data.email.lower()})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    user_doc = {
        "id": user_id,
        "email": data.email.lower(),
        "password_hash": hash_password(data.password),
        "name": data.name or data.email.split('@')[0],
        "created_at": now,
        "build_count": 0,
        "has_free_build": True
    }
    await db.users.insert_one(user_doc)
    token = create_token(user_id, data.email.lower())
    return {"token": token, "user": {"id": user_id, "email": data.email.lower(), "name": user_doc["name"], "created_at": now, "build_count": 0, "has_free_build": True}}

@api_router.post("/auth/login")
async def login(data: UserLogin):
    user = await db.users.find_one({"email": data.email.lower()})
    if not user or not verify_password(data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(user['id'], user['email'])
    return {"token": token, "user": {"id": user['id'], "email": user['email'], "name": user.get('name', ''), "created_at": user['created_at'], "build_count": user.get('build_count', 0), "has_free_build": user.get('has_free_build', True)}}

@api_router.get("/auth/me")
async def get_me(user=Depends(get_current_user)):
    build_count = await db.builds.count_documents({"user_id": user['id']})
    return {"id": user['id'], "email": user['email'], "name": user.get('name', ''), "created_at": user['created_at'], "build_count": build_count, "has_free_build": user.get('has_free_build', True)}


@api_router.post("/builds")
async def create_build(data: BuildCreate, user=Depends(get_current_user)):
    user_id = user['id']
    build_count = await db.builds.count_documents({"user_id": user_id})
    is_free = build_count == 0 and user.get('has_free_build', True)
    payment_status = "free" if is_free else "pending"
    build_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    build_doc = {"id": build_id, "user_id": user_id, "name": data.name, "description": data.description or "", "status": "draft", "is_free": is_free, "payment_status": payment_status, "price": 0.0 if is_free else 10.0, "created_at": now, "updated_at": now}
    await db.builds.insert_one(build_doc)
    if is_free:
        await db.users.update_one({"id": user_id}, {"$set": {"has_free_build": False}})
    await db.users.update_one({"id": user_id}, {"$inc": {"build_count": 1}})
    return {**build_doc}

@api_router.get("/builds")
async def get_builds(user=Depends(get_current_user)):
    return await db.builds.find({"user_id": user['id']}, {"_id": 0}).sort("created_at", -1).to_list(100)

@api_router.put("/builds/{build_id}")
async def edit_build(build_id: str, data: BuildEdit, user=Depends(get_current_user)):
    build = await db.builds.find_one({"id": build_id, "user_id": user['id']})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    update_fields = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if data.name is not None:
        update_fields["name"] = data.name
    if data.description is not None:
        update_fields["description"] = data.description
    await db.builds.update_one({"id": build_id}, {"$set": update_fields})
    return await db.builds.find_one({"id": build_id}, {"_id": 0})

@api_router.post("/builds/{build_id}/deploy")
async def deploy_build(build_id: str, user=Depends(get_current_user)):
    build = await db.builds.find_one({"id": build_id, "user_id": user['id']})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    if not build['is_free'] and build['payment_status'] not in ('paid', 'mock_paid', 'free'):
        raise HTTPException(status_code=402, detail="Payment required before deployment. $10.00 per build.")
    await db.builds.update_one({"id": build_id}, {"$set": {"status": "deployed", "updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"message": "Build deployed successfully", "status": "deployed"}

@api_router.post("/builds/{build_id}/pay")
async def pay_for_build(build_id: str, user=Depends(get_current_user)):
    build = await db.builds.find_one({"id": build_id, "user_id": user['id']})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    if build['is_free']:
        return {"message": "This build is free!", "payment_status": "free"}
    if build['payment_status'] in ('paid', 'mock_paid'):
        return {"message": "Already paid", "payment_status": build['payment_status']}
    await db.builds.update_one({"id": build_id}, {"$set": {"payment_status": "mock_paid", "updated_at": datetime.now(timezone.utc).isoformat()}})
    await db.payments.insert_one({"id": str(uuid.uuid4()), "build_id": build_id, "user_id": user['id'], "amount": 10.0, "currency": "USD", "status": "mock_completed", "provider": "mock_stripe", "created_at": datetime.now(timezone.utc).isoformat()})
    return {"message": "Payment successful (mock)", "payment_status": "mock_paid"}

@api_router.get("/pricing")
async def get_pricing():
    return {"plans": [{"name": "First Build", "price": 0, "price_label": "FREE", "description": "Your first build and deployment is completely free", "features": ["1 free build & deployment", "Unlimited edits on your build", "Partner in Crime AI (unlimited)", "Full-stack web & mobile apps"]}, {"name": "Per Build", "price": 10.0, "price_label": "$10.00", "description": "Each additional build after your first", "features": ["1 build & deployment", "Unlimited edits (always free)", "Partner in Crime AI (unlimited)", "Full-stack web & mobile apps", "All payment methods accepted"]}], "notes": ["First build is always free", "Edits to any build are always free", "AI Partner in Crime is always free to chat", "AI cannot assist with building until you pay for a build"]}


PARTNER_SYSTEM_MESSAGE = """You are Partner in Crime for maligeeAi. Be helpful and witty. Building full implementation code requires a paid/free build on the account; otherwise guide users to Dashboard."""

@api_router.post("/chat")
async def chat_with_ai(data: ChatMessage, user=Depends(get_optional_user)):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI service not configured")
    session_id = data.session_id or str(uuid.uuid4())
    user_id = user['id'] if user else 'anonymous'
    can_build = False
    if user:
        paid_builds = await db.builds.count_documents({"user_id": user['id'], "payment_status": {"$in": ["free", "paid", "mock_paid"]}})
        can_build = paid_builds > 0
    system_msg = PARTNER_SYSTEM_MESSAGE + ("\nUser may build code." if can_build else "\nUser has no builds yet; do not write full implementation code.")
    chat_key = f"{user_id}_{session_id}"
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=chat_key, system_message=system_msg)
        chat.with_model("openai", "gpt-4o")
        history = await db.chat_history.find({"session_id": session_id, "user_id": user_id}).sort("created_at", 1).to_list(50)
        for msg in history:
            chat.messages.append({"role": msg['role'], "content": msg['content']})
        response = await chat.send_message(UserMessage(text=data.message))
        now = datetime.now(timezone.utc).isoformat()
        await db.chat_history.insert_many([{"session_id": session_id, "user_id": user_id, "role": "user", "content": data.message, "created_at": now}, {"session_id": session_id, "user_id": user_id, "role": "assistant", "content": response, "created_at": now}])
        return {"response": response, "session_id": session_id}
    except Exception as e:
        logger.error(f"AI chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@api_router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, user=Depends(get_current_user)):
    return await db.chat_history.find({"session_id": session_id, "user_id": user['id']}, {"_id": 0}).sort("created_at", 1).to_list(100)

@api_router.get("/chat/sessions")
async def get_chat_sessions(user=Depends(get_current_user)):
    pipeline = [{"$match": {"user_id": user['id']}}, {"$group": {"_id": "$session_id", "last_message": {"$last": "$content"}, "last_time": {"$last": "$created_at"}, "count": {"$sum": 1}}}, {"$sort": {"last_time": -1}}, {"$limit": 20}]
    sessions = await db.chat_history.aggregate(pipeline).to_list(20)
    return [{"session_id": s["_id"], "last_message": s["last_message"][:80], "last_time": s["last_time"], "message_count": s["count"]} for s in sessions]


SEED_SHOWCASE = [{"mobile_image": "https://assets.emergent.sh/assets/showcase/Mob1.webp", "laptop_image": "https://assets.emergent.sh/assets/showcase/Laptop1.webp", "order": 1}, {"mobile_image": "https://assets.emergent.sh/assets/showcase/Mob2.webp", "laptop_image": "https://assets.emergent.sh/assets/showcase/Laptop2.webp", "order": 2}, {"mobile_image": "https://assets.emergent.sh/assets/showcase/Mob3.webp", "laptop_image": "https://assets.emergent.sh/assets/showcase/Laptop3.webp", "order": 3}, {"mobile_image": "https://assets.emergent.sh/assets/showcase/Mob4.webp", "laptop_image": "https://assets.emergent.sh/assets/showcase/Laptop4.webp", "order": 4}]
SEED_FEATURES = [{"icon": "monitor-smartphone", "title": "Build websites and mobile apps", "description": "Transform your ideas into fully functional websites and mobile apps.", "mockup_type": "library", "order": 1}, {"icon": "bot", "title": "Build custom agents", "description": "Create intelligent AI agents that automate tasks.", "mockup_type": "agent", "order": 2}, {"icon": "link", "title": "Build powerful integrations", "description": "Connect your apps to thousands of services and APIs.", "mockup_type": "integration", "order": 3}]

async def seed_data_internal():
    if await db.showcase.count_documents({}) == 0:
        for d in SEED_SHOWCASE:
            await db.showcase.insert_one({**d, "id": str(uuid.uuid4())})
    if await db.features.count_documents({}) == 0:
        for d in SEED_FEATURES:
            await db.features.insert_one({**d, "id": str(uuid.uuid4())})
    if await db.stats.count_documents({}) == 0:
        await db.stats.insert_one({"users_count": "3M+", "description": "users worldwide building & launching real applications in minutes."})

@api_router.get("/")
async def root():
    return {"message": "maligeeAi API is running"}

@api_router.get("/showcase", response_model=List[ShowcaseItem])
async def get_showcase():
    items = await db.showcase.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    if not items:
        await seed_data_internal()
        items = await db.showcase.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return items

@api_router.get("/features", response_model=List[Feature])
async def get_features():
    items = await db.features.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    if not items:
        await seed_data_internal()
        items = await db.features.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return items

@api_router.get("/stats", response_model=Stats)
async def get_stats():
    stats = await db.stats.find_one({}, {"_id": 0})
    if not stats:
        await seed_data_internal()
        stats = await db.stats.find_one({}, {"_id": 0})
    return stats or Stats()

@api_router.post("/waitlist", response_model=WaitlistEntry)
async def create_waitlist_entry(entry: WaitlistCreate):
    existing = await db.waitlist.find_one({"email": entry.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already on waitlist")
    obj = WaitlistEntry(**entry.model_dump())
    doc = obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.waitlist.insert_one(doc)
    return obj

@api_router.get("/waitlist/count")
async def get_waitlist_count():
    return {"count": await db.waitlist.count_documents({})}

@api_router.post("/seed")
async def seed_data():
    await seed_data_internal()
    return {"message": "Database seeded successfully"}


from routes.appmaker24 import register as register_appmaker24_routes
register_appmaker24_routes(api_router)

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
