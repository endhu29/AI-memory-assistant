import bcrypt
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from config import get_settings

settings = get_settings()

serializer  = URLSafeTimedSerializer(settings.SECRET_KEY)

SESSION_COOKIE = "eldercare_session"
MAX_AGE        = settings.SESSION_EXPIRE_MINUTES * 60   # seconds


def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def create_session_token(user_id: int) -> str:
    return serializer.dumps(user_id, salt="session")


def decode_session_token(token: str):
    """Returns user_id or None."""
    try:
        return serializer.loads(token, salt="session", max_age=MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None