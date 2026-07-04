from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, HealthLog
from app.services.health_checker import check_health_log, check_weight_change
from app.services.notification import notify_health_alert

router    = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/health-log", response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
    user: User  = Depends(get_current_user)
):
    logs = db.query(HealthLog).filter_by(user_id=user.id)\
        .order_by(HealthLog.log_date.desc()).all()
    return templates.TemplateResponse("health_log.html",
        {"request": request, "user": user, "logs": logs})


@router.post("/health-log/add")
async def add(
    request: Request,
    db: Session = Depends(get_db),
    user: User  = Depends(get_current_user)
):
    form = await request.form()

    def _int(f):
        v = form.get(f, "").strip()
        return int(v) if v else None

    def _float(f):
        v = form.get(f, "").strip()
        return float(v) if v else None

    log_date = datetime.strptime(form.get("log_date"), "%Y-%m-%d").date()

    log = HealthLog(
        user_id          = user.id,
        log_date         = log_date,
        weight_kg        = _float("weight_kg"),
        bp_systolic      = _int("bp_systolic"),
        bp_diastolic     = _int("bp_diastolic"),
        blood_sugar_mgdl = _int("blood_sugar_mgdl"),
        heart_rate_bpm   = _int("heart_rate_bpm"),
        spo2_pct         = _int("spo2_pct"),
        temperature_c    = _float("temperature_c"),
        health_feeling   = _int("health_feeling"),
        notes            = form.get("notes", "").strip() or None,
    )
    db.add(log)
    db.flush()

    violations = check_health_log(log)
    yesterday  = log_date - timedelta(days=1)
    prev_log   = db.query(HealthLog).filter_by(user_id=user.id, log_date=yesterday).first()
    violations += check_weight_change(log, prev_log)

    if violations and not log.alert_sent:
        notify_health_alert(db, user, violations)
        log.alert_sent = True

    db.commit()
    return RedirectResponse(url="/health-log", status_code=302)


@router.post("/health-log/{log_id}/delete")
def delete(log_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    log = db.query(HealthLog).filter_by(id=log_id, user_id=user.id).first()
    if log:
        db.delete(log)
        db.commit()
    return RedirectResponse(url="/health-log", status_code=302)