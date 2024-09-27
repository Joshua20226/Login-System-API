from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import aiomysql
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

def mongo_setup(signup_verify_collection, signin_verify_collection, 
                users_collection,dummy_users_collection, tokens_collection):
    
    # Restricting certain field to have duplicated entry
    signup_verify_collection.create_index('email', name='email', unique=True)
    signup_verify_collection.create_index('verification_code', name='verification_code', unique=True)
    signup_verify_collection.create_index('createdAt', name='createdAt', expireAfterSeconds=900)
    signin_verify_collection.create_index('email', name='email', unique=True)
    signin_verify_collection.create_index('verification_code', name='verification_code', unique=True)
    signin_verify_collection.create_index('createdAt', name='createdAt', expireAfterSeconds=900)
    users_collection.create_index('email', name='email', unique=True)
    users_collection.create_index('username', name='username', unique=True)
    users_collection.create_index('role', name='role')
    users_collection.create_index('createdAt', name='createdAt')
    
    dummy_users_collection.create_index('email', name='email', unique=True)
    dummy_users_collection.create_index('verification_code', name='verification_code', unique=True)
    dummy_users_collection.create_index('createdAt', name='createdAt', expireAfterSeconds=900)
    tokens_collection.create_index('refresh_token', name='refresh_token', unique=True)
    tokens_collection.create_index('issued_at', name='issued_at')
    tokens_collection.create_index('expires_at', name='expires_at')
    tokens_collection.create_index('revoked', name='revoked')
    
def return_mongo_collection():
    load_dotenv()

    db_url = os.getenv('MONGO_URL')
    client = MongoClient(db_url, server_api=ServerApi('1'))
    client = AsyncIOMotorClient(db_url)
    
    db = client['login']
    signup_verify_collection = db['signup_verify']
    signin_verify_collection = db['signin_verify']
    users_collection = db['users']
    dummy_users_collection = db['dummy_users']
    tokens_collection = db['tokens']
    
    mongo_setup(signup_verify_collection, signin_verify_collection, 
                users_collection, dummy_users_collection, tokens_collection)
    
    return (signup_verify_collection, signin_verify_collection, 
            users_collection, dummy_users_collection, tokens_collection)
    
    
async def mysql_setup():
    db_host = os.getenv('MYSQL_DB_HOST')
    db_port = os.getenv('MYSQL_DB_PORT')
    db_user = os.getenv('MYSQL_DB_USER')
    db_password = os.getenv('MONGO_DB_PASSWORD')
    
    connectionPool = await aiomysql.create_pool(host = db_host, port = db_port, user = db_user, password = db_password)
    return connectionPool

return_mongo_collection()