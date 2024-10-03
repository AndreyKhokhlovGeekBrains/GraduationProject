from jose import jwt
from pytz import timezone
from pydantic import BaseModel
import datetime


JWT_EXPIRE = 120
JWT_SECRET_KEY = "CRnQphHDIAW4CjAiMy1fQRi2u05m1LQ0gySSFDIOPJdseknNIYQCR2V3zmJTGrHJvYpG5WRFBflY7DuUQR23fOpqYS8nmu8dWtjpU"
ALGORITHM = "HS256"


class TokenPayload(BaseModel):
    id: int
    email: str
    username: str
    expire: str

def create_token(user_id: int, user_email: str, username: str) -> str:
    expire = datetime.datetime.now(timezone('UTC')) + datetime.timedelta(minutes=int(JWT_EXPIRE))
    data = TokenPayload(id=user_id, email=user_email, username=username, expire=str(expire))
    encoded_token = jwt.encode(data.model_dump(), JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_token

def decode_token(token: str) -> TokenPayload:
    try:
        decoded_jwt = jwt.decode(token, JWT_SECRET_KEY, algorithms=ALGORITHM)
        return TokenPayload(**decoded_jwt)
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.JWTError:
        raise ValueError("Invalid token")
