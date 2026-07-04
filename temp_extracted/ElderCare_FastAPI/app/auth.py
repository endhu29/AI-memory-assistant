from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer  = URLSafeTimedSerializer(settings.SECRET_KEY)

SESSION_COOKIE = "eldercare_session"
MAX_AGE        = settings.SESSION_EXPIRE_MINUTES * 60   # seconds


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_session_token(user_id: int) -> str:
    return serializer.dumps(user_id, salt="session")


def decode_session_token(token: str):
    """Returns user_id or None."""
    try:
        return serializer.loads(token, salt="session", max_age=MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None