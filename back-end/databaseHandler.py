from databaseSetup import return_mongo_collection 
from datetime import datetime, timedelta
import random
from pymongo import errors
from sendEmail import sendEmail
from tokenHandler import create_access_token, create_refresh_token
import os
from dotenv import load_dotenv
from bson import ObjectId

def main():
    load_dotenv()
    global signup_verify_collection, signin_verify_collection, \
            users_collection, posts_collection, comments_collection, \
            dummy_users_collection, tokens_collection
            
    (signup_verify_collection, signin_verify_collection, 
     users_collection, posts_collection, comments_collection, 
     dummy_users_collection, tokens_collection) = return_mongo_collection()

# Send verification code when signing in or signing up 
async def send_verification_code(email, mode):
    if mode not in {'signup', 'signin'}:
        raise ValueError(f'Invalid mode for sending verification code. Allowed values are "signup" or "signin", your mode is {mode}')
    
    if mode == 'signup':
        collection = signup_verify_collection
    else:
        collection = signin_verify_collection
        
    # Check if email exists before sending for signing in
    # Or if user already exists for signing up
    result = await users_collection.find_one({'email': email})
    if mode == 'signin':
        if not result:
            return 400, {'message': 'Account not found'}
    else:
        if result:
            return 400, {'message': 'Email already registered, please sign in or use a different email'}
    
    # Check if a verification code has already been sent
    result = await collection.find_one({'email': email})
    if result:
        return 400, {'message': 'A verification code has already been sent to your email'}
    
    print('generating verify code')
    # Insert verification code to MongoDB     OPTIONS: ['signup', 'signin']
    valid_verification_code = False
    while valid_verification_code == False:
        verification_code = ''
        for _ in range(8):
            verification_code += str(random.randint(0, 9))
        document = {'email': email, 'verification_code': verification_code, 'createdAt': datetime.utcnow()}
        try:
            await collection.insert_one(document)
            valid_verification_code = True
        except errors.DuplicateKeyError:
            pass
    
    # Send email containing the verification code
    print('sending email')
    sendEmail('Your email verify code is {}'.format(verification_code), email)
    print('finsih sending email')
    return 200, {'message': 'We have sent the verify code to your gmail, please verify it'}

# Validate the verification code before signing in or signing up
async def validate_verification_code(email, verification_code, mode):
    if mode not in {'signup', 'signin'}:
        raise ValueError(f'Invalid mode for sending verification code. Allowed values are "signup" or "signin", your mode is {mode}')
    
    # Check MongoDB for correct verification code
    if mode == 'signup':
        collection = signup_verify_collection
    else:
        collection = signin_verify_collection
        
    result = await collection.find_one({'email': email})
    if result:
        db_verification_code = result.get('verification_code')
        if db_verification_code != verification_code:
            return 400, {'message': 'Incorrect verification code, please try again'}
    else:
        return 400, {'message': 'Verification code expired, please verify your email again'}
    
    
    # Delete verification code from db
    result = await collection.delete_one({"email": email, "verification_code": verification_code})
    if result.deleted_count <= 0:
        return 400, {'message': "Document doesn't exist"}
    return 200, {'message': 'Correct verification code'}


async def signupDummy(email, verification_code):
    # Validate verification code
    status_code, message = await validate_verification_code(email, verification_code, 'signup')
    if status_code != 200:
        return status_code, message
    
    # Create dummy user without username in a separate collection first for signup
    try:
        await dummy_users_collection.insert_one({'email': email, 'verification_code': verification_code, 'createdAt': datetime.utcnow()})
    except errors.DuplicateKeyError:
        return 400, {'message': 'You have already signed up, please create an username'}

    return 200, {'message': 'Correct verification code'}
    
    
# Sign up, ask for username and create user. 
async def signup(email, username, verification_code, IP):
    # Check dummy user from a separate collection to prevent from expiring and delete the document
    result = await dummy_users_collection.find_one_and_delete({'email': email, 'verification_code': verification_code})
    if not result:
        return 400, {'message': 'User not found, please signup'}

    # Prevent duplicated email 
    if await users_collection.find_one({'email': email}):
        return 400, {'message': 'Email already registered, please sign in or use a different email'}
    
    # Insert user
    try:
        await users_collection.insert_one({'email': email, 'username': username, 'createdAt': datetime.utcnow()})
    except errors.DuplicateKeyError:
        return 400, {'message': 'Username already exists, please choose another one'}
    
    # Generate token for login
    status_code, message = await generate_token(email, IP)
    if status_code == 400:
        return status_code, message
    message['message'] = 'User created successfully'
    return status_code, message
    
    return 200, {'message': 'success'}

# Sign in
async def signin(email: str, verification_code: str, IP):
    # Validate verification code
    status_code, message = await validate_verification_code(email, verification_code, 'signin')
    if status_code != 200:
        return status_code, message
    
    # Generate token for login
    status_code, message = await generate_token(email, IP)
    if status_code == 400:
        return status_code, message
    message['message'] = 'Log in successfully'
    return status_code, message

# Generate both access and refresh token 
async def generate_token(email: str, IP):
    user = await users_collection.find_one({'email': email})
    if not user:
        return 400, {'message': 'User not found, please signup'}
    user_id = user['_id']
    
    # Generate session code 
    access_token = create_access_token({'sub': email, 'ip': IP})
    refresh_token = create_refresh_token(user_id, IP)
    
    # Store session code
    await store_token(refresh_token, user_id)
    return 200, {'access_token': access_token, 'token_type': 'bearer', 'refresh_token': refresh_token}

# Store all refresh token in MongoDB for revoking later on.
async def store_token(refresh_token: str, user_id: ObjectId):
    await tokens_collection.insert_one({
        'user_id': user_id,
        'refresh_token': refresh_token,
        'issued_at': datetime.utcnow(),
        'expires_at': datetime.utcnow() + timedelta(days=int(os.getenv('REFRESH_TOKEN_EXPIRES_DAY'))),
        'revoked': False
    })

async def revoke_token(refresh_token: str):
    await tokens_collection.update_one(
        {'refresh_token': refresh_token},
        {'$set': {'revoked': True}}
    )
    
async def is_token_valid(refresh_token: str):
    token = await tokens_collection.find_one({'refresh_token': refresh_token, 'revoked': False})
    return token is not None

async def is_access_token_valid(user_id: str):
    result = await users_collection.find_one({'_id': user_id})
    if not result:
        return False
    return True

async def add_posts(title, role, description):
    pass