import hashlib
from database.auth_model import create_user, authenticate_user

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    hashed = hash_password(password)
    create_user(username, hashed)

def login(username, password):
    hashed = hash_password(password)
    return authenticate_user(username, hashed)
