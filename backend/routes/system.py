from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(prefix='/api/system', tags=['system'])

@router.get('/health')
async def health():
    return {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
