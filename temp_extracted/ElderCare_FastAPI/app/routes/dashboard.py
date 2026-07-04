from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Appointment, DoseLog, HealthLog

router    = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session   = Depends(get_db),
    user: User    = Depends(get_current_user)
):
    today       = date.today()
    now         = datetime.utcnow()
    today_start = datetime.combine(today, datetime.min.time())
    today_end   = datetime.combine(today, datetime.max.time())

    pending_doses = db.query(DoseLog).filter(
        DoseLog.user_id      == user.id,
        DoseLog.scheduled_dt.between(today_start, today_end),
        DoseLog.status       == "pending"
    ).count()

    total_doses = db.query(DoseLog).filter(
        DoseLog.user_id      == user.id,
        DoseLog.scheduled_dt.between(today_start, today_end)
    ).count()

    next_appt = db.query(Appointment).filter(
        Appointment.user_id        == user.id,
        Appointment.status         == "Scheduled",
        Appointment.appointment_dt >= now
    ).order_by(Appointment.appointment_dt.asc()).first()

    latest_health = db.query(HealthLog).filter_by(user_id=user.id)\
        .order_by(HealthLog.log_date.desc()).first()

    recent_logs = db.query(HealthLog).filter_by(user_id=user.id)\
        .order_by(HealthLog.log_date.desc()).limit(5).all()

    upcoming_appts = db.query(Appointment).filter(
        Appointment.user_id        == user.id,
        Appointment.status         == "Scheduled",
        Appointment.appointment_dt >= now
    ).order_by(Appointment.appointment_dt.asc()).limit(3).all()

    return templates.TemplateResponse("dashboard.html", {
        "request":       request,
        "user":          user,
        "today":         today,
        "pending_doses": pending_doses,
        "total_doses":   total_doses,
        "next_appt":     next_appt,
        "latest_health": latest_health,
        "recent_logs":   recent_logs,
        "upcoming_appts":upcoming_appts,
    })