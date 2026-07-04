from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import decode_session_token, SESSION_COOKIE
from app.models import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    FastAPI dependency — reads the session cookie and returns the logged-in User.
    Raises 401 (redirected to login by exception handler) if not authenticated.
    """
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_id = decode_session_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    """Returns User or None — used for pages that work both logged-in and logged-out."""
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None