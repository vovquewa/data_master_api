from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.settings import settings

security = HTTPBearer()

API_TOKEN = settings.API_TOKEN


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    api_token = credentials.credentials
    if api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token or missing token")
    return api_token
