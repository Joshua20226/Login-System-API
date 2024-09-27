# import libary
from fastapi.responses import JSONResponse
import databaseHandler
from fastapi import FastAPI, HTTPException, Request, Query, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from datetime import datetime
from pydantic import BaseModel
from tokenHandler import verify_token, decode_token, create_access_token
import subprocess
import sys
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('server_logs')
fh = logging.FileHandler('server_logs.log')
fh.setLevel(logging.INFO)
logger.addHandler(fh)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    date = str(datetime.now())
    message = await call_next(request)
    client_host = request.client.host
    log_msg = f"{request.method} {request.url.path} - IP: {client_host} - Date: {date}"
    logger.info(log_msg)
    return message

@app.on_event('startup')
async def on_startup():
    databaseHandler.main()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "Json Format Invalid", "errors": exc.errors()},
    )
    
class UsersVerifyModel(BaseModel):
    email: str
    mode: str

class UsersSignupVerifyModel(BaseModel):
    email: str
    verification_code: str
    
class UsersSignupModel(BaseModel):
    email: str
    username: str
    verification_code: str
    
class UsersSigninModel(BaseModel):
    email: str
    verification_code: str
    

@app.post('/users/verify')
async def users_verify(requestInfo: UsersVerifyModel):
    email = requestInfo.email
    mode = requestInfo.mode
    
    print('send verification code')
    status_code, message = await databaseHandler.send_verification_code(email, mode)                
    message = JSONResponse(content = message, status_code=status_code)
    return message
    
# Front-end should save the verification code as cookie for signup completion
@app.post('/users/signup/verify')
async def signup_verify(requestInfo: UsersSignupVerifyModel):
    email = requestInfo.email
    verification_code = requestInfo.verification_code

    status_code, message = await databaseHandler.signupDummy(email, verification_code)
    return JSONResponse(content=message, status_code=status_code)
    
@app.post('/users/signup')
async def signup(request: Request, requestInfo: UsersSignupModel):
    email = requestInfo.email
    username = requestInfo.username
    verification_code = requestInfo.verification_code

    status_code, message = await databaseHandler.signup(email, username, verification_code, request.client.host)
    return JSONResponse(content=message, status_code=status_code)


@app.post('/users/signin')
async def signin(request:Request, requestInfo: UsersSigninModel):
    email = requestInfo.email
    verification_code = requestInfo.verification_code

    status_code, message = await databaseHandler.signin(email, verification_code, request.client.host)
    return JSONResponse(content=message, status_code=status_code)
    
@app.post('/refresh')
async def refresh_token(refresh_token: str):
    if not await databaseHandler.is_token_valid(refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    decoded_token = decode_token(refresh_token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token.')
    
    access_token = create_access_token(data={'sub': decoded_token['sub']})
    message = {'access_token': access_token, 'token_type': 'bearer'}
    return JSONResponse(content=message, status_code=200)
    
     
@app.post('/posts/add')
async def add_posts(request: Request, token: str = Depends(oauth2_scheme)):
    result = token.verify_token(token, request.client.host)
    if type(result) == list:
        print(result)
        raise HTTPException(status_code=result[0], detail=result[1], headers=result[2])
    
    payload = result
    user_id = payload['user_id']
    result = await databaseHandler.is_access_token_valid(user_id)
    if not result:
        raise HTTPException(400, 'Invalid token', {'WWW-Authenticate': 'Bearer'})
    try:
        data = await request.json()
        title = data.get('titleInput')
        role = data.get('roleOptionInput')
        description = data.get('descriptionInput')
    except:
        return HTTPException(400, 'Json Format Invalid.')
    
    message = await databaseHandler.add_posts(title, role, description)
    

if __name__ == '__main__':
    load_dotenv()
    subprocess.run([sys.executable, "-m", "uvicorn", 'main:app', "--host", os.getenv('SERVER_HOST'), "--port", "8088", "--reload"])
    # https://www.uvicorn.org/deployment/#gunicorn
