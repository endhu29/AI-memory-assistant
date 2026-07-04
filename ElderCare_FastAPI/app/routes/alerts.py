from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, AlertLog
from app.services.notification import send_email

router    = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/alerts", response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
    user: User  = Depends(get_current_user)
):
    logs = db.query(AlertLog).filter_by(user_id=user.id)\
        .order_by(AlertLog.created_at.desc()).all()
    return templates.TemplateResponse(request, "alerts.html",
        {"user": user, "logs": logs})


@router.post("/alerts/send")
def send_manual(
    to_email: str = Form(...),
    subject:  str = Form(...),
    message:  str = Form(...),
    urgent:   str = Form(None),
    db: Session   = Depends(get_db),
    user: User    = Depends(get_current_user)
):
    send_email(db, user.id, to_email, subject, message,
               "custom", urgent=urgent == "on")
    return RedirectResponse(url="/alerts", status_code=302)


@router.post("/alerts/{log_id}/resend")
def resend(log_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    log = db.query(AlertLog).filter_by(id=log_id, user_id=user.id).first()
    if log:
        send_email(db, user.id, log.sent_to_email,
                   "Resent: Alert", log.message, log.alert_type)
    return RedirectResponse(url="/alerts", status_code=302)