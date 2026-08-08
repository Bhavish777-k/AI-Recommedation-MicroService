# config/auth.py
import os
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()
FASTAPI_API_KEY = os.getenv("FASTAPI_API_KEY")

def validate_api_key(x_api_key: str | None = Header(None)):
    if FASTAPI_API_KEY:
        if not x_api_key or x_api_key != FASTAPI_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key"
            )
    return True
