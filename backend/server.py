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

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT config
JWT_SECRET = os.environ.get('JWT_SECRET', 'maligeeai-secret-key-change-in-prod-2025')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_HOURS = 72

# LLM config
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer(auto_error=False)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════

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
    status: str  # draft, deployed, failed
    is_free: bool
    payment_status: str  # free, pending, paid, mock_paid
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


# ═══════════════════════════════════════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
# AUTH ROUTES
# ═══════════════════════════════════════════════════════════════

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
    logger.info(f"New user signup: {data.email}")
    return {
        "token": token,
        "user": {
            "id": user_id,
            "email": data.email.lower(),
            "name": user_doc["name"],
            "created_at": now,
            "build_count": 0,
            "has_free_build": True
        }
    }

@api_router.post("/auth/login")
async def login(data: UserLogin):
    user = await db.users.find_one({"email": data.email.lower()})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user['id'], user['email'])
    return {
        "token": token,
        "user": {
            "id": user['id'],
            "email": user['email'],
            "name": user.get('name', ''),
            "created_at": user['created_at'],
            "build_count": user.get('build_count', 0),
            "has_free_build": user.get('has_free_build', True)
        }
    }

@api_router.get("/auth/me")
async def get_me(user=Depends(get_current_user)):
    build_count = await db.builds.count_documents({"user_id": user['id']})
    return {
        "id": user['id'],
        "email": user['email'],
        "name": user.get('name', ''),
        "created_at": user['created_at'],
        "build_count": build_count,
        "has_free_build": user.get('has_free_build', True)
    }


# ═══════════════════════════════════════════════════════════════
# BUILD / BILLING ROUTES
# ═══════════════════════════════════════════════════════════════

@api_router.post("/builds")
async def create_build(data: BuildCreate, user=Depends(get_current_user)):
    user_id = user['id']
    build_count = await db.builds.count_documents({"user_id": user_id})

    # First build is free
    is_free = build_count == 0 and user.get('has_free_build', True)
    payment_status = "free" if is_free else "pending"

    build_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    build_doc = {
        "id": build_id,
        "user_id": user_id,
        "name": data.name,
        "description": data.description or "",
        "status": "draft",
        "is_free": is_free,
        "payment_status": payment_status,
        "price": 0.0 if is_free else 10.0,
        "created_at": now,
        "updated_at": now
    }
    await db.builds.insert_one(build_doc)

    # If first build, mark user as used free build
    if is_free:
        await db.users.update_one({"id": user_id}, {"$set": {"has_free_build": False}})

    await db.users.update_one({"id": user_id}, {"$inc": {"build_count": 1}})
    logger.info(f"Build created: {build_id} for user {user_id} (free={is_free})")

    return {
        "id": build_id,
        "user_id": user_id,
        "name": data.name,
        "description": data.description or "",
        "status": "draft",
        "is_free": is_free,
        "payment_status": payment_status,
        "price": 0.0 if is_free else 10.0,
        "created_at": now,
        "updated_at": now
    }

@api_router.get("/builds")
async def get_builds(user=Depends(get_current_user)):
    builds = await db.builds.find({"user_id": user['id']}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return builds

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
    updated = await db.builds.find_one({"id": build_id}, {"_id": 0})
    return updated

@api_router.post("/builds/{build_id}/deploy")
async def deploy_build(build_id: str, user=Depends(get_current_user)):
    build = await db.builds.find_one({"id": build_id, "user_id": user['id']})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")

    # Check payment
    if not build['is_free'] and build['payment_status'] not in ('paid', 'mock_paid', 'free'):
        raise HTTPException(status_code=402, detail="Payment required before deployment. $10.00 per build.")

    await db.builds.update_one({"id": build_id}, {"$set": {
        "status": "deployed",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }})
    return {"message": "Build deployed successfully", "status": "deployed"}

@api_router.post("/builds/{build_id}/pay")
async def pay_for_build(build_id: str, user=Depends(get_current_user)):
    """Mock payment endpoint - will be replaced with Stripe later"""
    build = await db.builds.find_one({"id": build_id, "user_id": user['id']})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")

    if build['is_free']:
        return {"message": "This build is free!", "payment_status": "free"}

    if build['payment_status'] in ('paid', 'mock_paid'):
        return {"message": "Already paid", "payment_status": build['payment_status']}

    # MOCK PAYMENT - Replace with Stripe checkout later
    await db.builds.update_one({"id": build_id}, {"$set": {
        "payment_status": "mock_paid",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }})

    # Log the mock payment
    await db.payments.insert_one({
        "id": str(uuid.uuid4()),
        "build_id": build_id,
        "user_id": user['id'],
        "amount": 10.0,
        "currency": "USD",
        "status": "mock_completed",
        "provider": "mock_stripe",
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    logger.info(f"Mock payment for build {build_id} by user {user['id']}")
    return {"message": "Payment successful (mock)", "payment_status": "mock_paid"}

@api_router.post("/builds/{build_id}/share")
async def create_share_link(build_id: str, user=Depends(get_current_user)):
    build = await db.builds.find_one({"id": build_id, "user_id": user['id']})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    if build['status'] != 'deployed':
        raise HTTPException(status_code=400, detail="Only deployed builds can be shared")
    slug = build.get('share_slug')
    if not slug:
        slug = uuid.uuid4().hex[:8]
        await db.builds.update_one({"id": build_id}, {"$set": {"share_slug": slug}})
    return {"share_slug": slug}

@api_router.get("/share/{slug}")
async def get_shared_build(slug: str):
    build = await db.builds.find_one({"share_slug": slug}, {"_id": 0})
    if not build or build.get('status') != 'deployed':
        raise HTTPException(status_code=404, detail="Shared build not found")
    owner = await db.users.find_one({"id": build['user_id']}, {"_id": 0})
    return {
        "name": build['name'],
        "description": build.get('description', ''),
        "status": build['status'],
        "created_at": build['created_at'],
        "owner_name": owner.get('name', 'A maligeeAi builder') if owner else 'A maligeeAi builder'
    }

@api_router.get("/pricing")
async def get_pricing():
    return {
        "plans": [
            {
                "name": "First Build",
                "price": 0,
                "price_label": "FREE",
                "description": "Your first build and deployment is completely free",
                "features": [
                    "1 free build & deployment",
                    "Unlimited edits on your build",
                    "Partner in Crime AI (unlimited)",
                    "Full-stack web & mobile apps"
                ]
            },
            {
                "name": "Per Build",
                "price": 10.0,
                "price_label": "$10.00",
                "description": "Each additional build after your first",
                "features": [
                    "1 build & deployment",
                    "Unlimited edits (always free)",
                    "Partner in Crime AI (unlimited)",
                    "Full-stack web & mobile apps",
                    "All payment methods accepted"
                ]
            }
        ],
        "notes": [
            "First build is always free",
            "Edits to any build are always free",
            "AI Partner in Crime is always free to chat",
            "AI cannot assist with building until you pay for a build"
        ]
    }


# ═══════════════════════════════════════════════════════════════
# AI "PARTNER IN CRIME" ROUTES
# ═══════════════════════════════════════════════════════════════

# Store active chat sessions
chat_sessions = {}

PARTNER_SYSTEM_MESSAGE = """You are "Partner in Crime" — an AI assistant for maligeeAi. You are helpful, witty, and unfiltered. You speak candidly and don't hold back. You can discuss any topic openly.

Key rules:
1. You are FREE to use — always remind users of this if they ask
2. You can help with general questions, web research, brainstorming, coding concepts, anything
3. CRITICAL RULE: If the user asks you to help BUILD something (generate code, create an app, build a project, write implementation code), you MUST check if they have a paid build. If they haven't paid for a build yet, respond with: "I'd love to help you build that! But here's the deal — you need to pay $10 for a build first. Your first build is FREE though! Head to the Dashboard and create your first build. After that, I'm all yours for building. 🔥"
4. You CAN help with: explaining code, debugging concepts, general coding questions, brainstorming ideas, web research, any topic
5. You CANNOT help with: actually writing/generating full implementation code for builds until they've paid
6. Be conversational, use emojis occasionally, be a real partner in crime
7. If someone asks who you are, say "I'm Partner in Crime, your AI sidekick on maligeeAi. I'm here to help you with anything — well, almost anything until you pay for a build 😏"
"""

@api_router.post("/chat")
async def chat_with_ai(data: ChatMessage, user=Depends(get_optional_user)):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI service not configured")

    session_id = data.session_id or str(uuid.uuid4())
    user_id = user['id'] if user else 'anonymous'

    # Check if user has paid builds (to determine if AI can help build)
    has_paid_build = False
    can_build = False
    if user:
        paid_builds = await db.builds.count_documents({
            "user_id": user['id'],
            "payment_status": {"$in": ["free", "paid", "mock_paid"]}
        })
        has_paid_build = paid_builds > 0
        can_build = has_paid_build

    # Adjust system message based on payment status
    system_msg = PARTNER_SYSTEM_MESSAGE
    if can_build:
        system_msg += "\n\nIMPORTANT: This user HAS paid for builds. You CAN help them build, write code, and create implementations. Go all out!"
    else:
        system_msg += "\n\nIMPORTANT: This user has NOT paid for any builds yet. Do NOT write implementation code for them. Guide them to create a build first."

    # Create or reuse chat session
    chat_key = f"{user_id}_{session_id}"

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=chat_key,
            system_message=system_msg
        )
        chat.with_model("openai", "gpt-4o")

        # Load chat history from DB
        history = await db.chat_history.find(
            {"session_id": session_id, "user_id": user_id}
        ).sort("created_at", 1).to_list(50)

        for msg in history:
            if msg['role'] == 'user':
                chat.messages.append({"role": "user", "content": msg['content']})
            elif msg['role'] == 'assistant':
                chat.messages.append({"role": "assistant", "content": msg['content']})

        user_message = UserMessage(text=data.message)
        response = await chat.send_message(user_message)

        # Save to chat history
        now = datetime.now(timezone.utc).isoformat()
        await db.chat_history.insert_many([
            {
                "session_id": session_id,
                "user_id": user_id,
                "role": "user",
                "content": data.message,
                "created_at": now
            },
            {
                "session_id": session_id,
                "user_id": user_id,
                "role": "assistant",
                "content": response,
                "created_at": now
            }
        ])

        return {"response": response, "session_id": session_id}

    except Exception as e:
        logger.error(f"AI chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@api_router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, user=Depends(get_current_user)):
    history = await db.chat_history.find(
        {"session_id": session_id, "user_id": user['id']},
        {"_id": 0}
    ).sort("created_at", 1).to_list(100)
    return history

@api_router.get("/chat/sessions")
async def get_chat_sessions(user=Depends(get_current_user)):
    pipeline = [
        {"$match": {"user_id": user['id']}},
        {"$group": {
            "_id": "$session_id",
            "last_message": {"$last": "$content"},
            "last_time": {"$last": "$created_at"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"last_time": -1}},
        {"$limit": 20}
    ]
    sessions = await db.chat_history.aggregate(pipeline).to_list(20)
    return [{"session_id": s["_id"], "last_message": s["last_message"][:80], "last_time": s["last_time"], "message_count": s["count"]} for s in sessions]


# ═══════════════════════════════════════════════════════════════
# LANDING PAGE DATA ROUTES
# ═══════════════════════════════════════════════════════════════

SEED_SHOWCASE = [
    {"mobile_image": "https://assets.emergent.sh/assets/showcase/Mob1.webp", "laptop_image": "https://assets.emergent.sh/assets/showcase/Laptop1.webp", "order": 1},
    {"mobile_image": "https://assets.emergent.sh/assets/showcase/Mob2.webp", "laptop_image": "https://assets.emergent.sh/assets/showcase/Laptop2.webp", "order": 2},
    {"mobile_image": "https://assets.emergent.sh/assets/showcase/Mob3.webp", "laptop_image": "https://assets.emergent.sh/assets/showcase/Laptop3.webp", "order": 3},
    {"mobile_image": "https://assets.emergent.sh/assets/showcase/Mob4.webp", "laptop_image": "https://assets.emergent.sh/assets/showcase/Laptop4.webp", "order": 4},
]

SEED_FEATURES = [
    {"icon": "monitor-smartphone", "title": "Build websites and mobile apps", "description": "Transform your ideas into fully functional websites and mobile apps with instant deployment, seamless data connections, and powerful scalability.", "mockup_type": "library", "order": 1},
    {"icon": "bot", "title": "Build custom agents", "description": "Create intelligent AI agents that automate tasks, answer questions, and interact with your users. Deploy them anywhere with just a few clicks.", "mockup_type": "agent", "order": 2},
    {"icon": "link", "title": "Build powerful integrations", "description": "Connect your apps to thousands of services and APIs. Build complex workflows with ease using our integration framework.", "mockup_type": "integration", "order": 3},
]

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
    count = await db.waitlist.count_documents({})
    return {"count": count}

@api_router.post("/seed")
async def seed_data():
    await seed_data_internal()
    return {"message": "Database seeded successfully"}


# Include router & middleware
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
