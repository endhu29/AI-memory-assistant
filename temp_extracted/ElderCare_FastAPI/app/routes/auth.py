from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import User
from app.auth import hash_password, verify_password, create_session_token, SESSION_COOKIE, MAX_AGE

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    return RedirectResponse(url="/login")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("auth/login.html",
            {"request": request, "error": "Invalid username or password."}, status_code=401)

    user.last_login = datetime.utcnow()
    db.commit()

    token    = create_session_token(user.id)
    redirect = RedirectResponse(url="/dashboard", status_code=302)
    redirect.set_cookie(SESSION_COOKIE, token, max_age=MAX_AGE, httponly=True, samesite="lax")
    return redirect


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request, "error": None})


@router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    username: str = Form(...),
    email: str    = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse("auth/register.html",
            {"request": request, "error": "Passwords do not match."})

    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("auth/register.html",
            {"request": request, "error": "Username already taken."})

    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("auth/register.html",
            {"request": request, "error": "Email already registered."})

    user = User(username=username, email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    return RedirectResponse(url="/login?registered=1", status_code=302)


@router.get("/logout")
def logout():
    redirect = RedirectResponse(url="/login", status_code=302)
    redirect.delete_cookie(SESSION_COOKIE)
    return redirect