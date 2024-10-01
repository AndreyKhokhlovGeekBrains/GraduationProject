from argparse import ArgumentError

from jose import jwt
from uuid import uuid4

from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, Field, constr
from pydantic import BaseModel
from datetime import datetime, date


ALGORITHMS = "HS256"
SECRET_KEY = "df40bb13e3125376d80767950a4499e165f2be7c35728768f2b9e4a8a8d39675"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
token_blacklist = {}

class UserIn(BaseModel):
    name: constr(max_length=32) = Field(..., description="Name of the user")
    email: constr(max_length=128) = Field(..., description="Email of the user")
    password: constr(min_length=8, max_length=255) = Field(..., description="Password with minimum 8 characters")  # Added min_length for security
    age: int = Field(None, gt=0, description="Age must be a positive integer")  # Age should be greater than 0
    birthdate: date = Field(..., description="Birthdate in YYYY-MM-DD format")
    phone: str = Field(..., pattern=r'^\+?\d{7,20}$', description="Phone number with 7-20 digits, optional + for international format")
    agreement: bool = Field(None, description="Check box")


def create_jwt(user: UserIn, user_id) -> str:
    expire = datetime.now() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    user_data = user.model_dump()

    data = {
        "id": user_id,
        "username": user_data["name"],
        "email": user_data["email"],
        "exp": expire,
        "jti": str(uuid4())
    }

    # Создание JWT
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHMS)
    return token


def revoke_token(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHMS)
    jti = payload["jti"]
    token_blacklist[jti] = True

def is_token_revoked(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHMS)
    jti = payload["jti"]
    return jti in token_blacklist


def decode_jwt_token(token):
    try:
        decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHMS)
        return decoded_token
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.JWTError:
        return {"error": "Invalid token"}
    except AttributeError:
        print("Attribute error")


def check_jwt(token):
    decoded_token = None
    if token:
        if not is_token_revoked(token):
            decoded_token = decode_jwt_token(token)

    return decoded_token


def update_jwt(user: UserIn, user_id, token):
    revoke_token(token)
    token = create_jwt(user=user, user_id=user_id)

    return token
