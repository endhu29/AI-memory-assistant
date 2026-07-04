import os, shutil
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Profile
from config import get_settings

router    = APIRouter()
templates = Jinja2Templates(directory="templates")
settings  = get_settings()

ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}


@router.get("/profile", response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
    user: User  = Depends(get_current_user)
):
    return templates.TemplateResponse("profile.html",
        {"request": request, "user": user, "profile": user.profile})


@router.post("/profile/save")
async def save(
    request: Request,
    db: Session = Depends(get_db),
    user: User  = Depends(get_current_user)
):
    form  = await request.form()
    profile = user.profile or Profile(user_id=user.id)

    profile.full_name               = form.get("full_name", "").strip()
    profile.date_of_birth           = datetime.strptime(form.get("date_of_birth"), "%Y-%m-%d").date()
    profile.gender                  = form.get("gender", "")
    profile.blood_group             = form.get("blood_group", "").strip() or None
    profile.phone                   = form.get("phone", "").strip() or None
    profile.address                 = form.get("address", "").strip() or None
    profile.known_conditions        = form.get("known_conditions", "").strip() or None
    profile.allergies               = form.get("allergies", "").strip() or None
    profile.primary_doctor_name     = form.get("primary_doctor_name", "").strip() or None
    profile.primary_doctor_phone    = form.get("primary_doctor_phone", "").strip() or None
    profile.guardian_name           = form.get("guardian_name", "").strip()
    profile.guardian_relationship   = form.get("guardian_relationship", "").strip() or None
    profile.guardian_phone          = form.get("guardian_phone", "").strip() or None
    profile.guardian_email          = form.get("guardian_email", "").strip()
    profile.emergency_contact_name  = form.get("emergency_contact_name", "").strip() or None
    profile.emergency_contact_phone = form.get("emergency_contact_phone", "").strip() or None

    # Photo upload
    photo = form.get("photo")
    if photo and hasattr(photo, "filename") and photo.filename:
        ext = photo.filename.rsplit(".", 1)[-1].lower()
        if ext in ALLOWED:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            filename = f"user_{user.id}_{photo.filename}"
            dest     = os.path.join(settings.UPLOAD_DIR, filename)
            with open(dest, "wb") as f:
                shutil.copyfileobj(photo.file, f)
            profile.photo_path = f"{settings.UPLOAD_DIR}/{filename}"

    if not profile.id:
        db.add(profile)
    db.commit()
    return RedirectResponse(url="/profile", status_code=302)