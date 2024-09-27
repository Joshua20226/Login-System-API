import jwt
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()
SECRET_KEY = os.getenv('TOKEN_SECRET_KEY')
ALGORITHM = "HS256"

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRES_MIN'))) 
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: ObjectId, IP):
    expire = datetime.utcnow() + timedelta(days=int(os.getenv('REFRESH_TOKEN_EXPIRES_DAY')))
    encoded_jwt = jwt.encode({'user_id': str(user_id), 'ip': IP, 'exp': expire}, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token if decoded_token["exp"] >= datetime.utcnow().timestamp() else None
    except jwt.PyJWTError:
        return None
    
def verify_token(token: str, IP):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user_ip = payload.get('ip')
        if user_id is None or user_ip is None:
            return [401, 'Invalid token', {'WWW-Authenticate': 'Bearer'}]
        
        # IP doesn't match
        if user_ip != IP:
            return [401, 'IP address mismatch', 
                    {'WWW-Authenticate': 'Bearer realm="IP mismatch", error="invalid_token", error_description="IP address does not match"'}]
        return payload
    except jwt.ExpiredSignatureError:
        return [401, 'Token expired', {"WWW-Authenticate": "Bearer"}]

    except jwt.InvalidTokenError:
        return [401, 'Invalid token', {"WWW-Authenticate": "Bearer"}]