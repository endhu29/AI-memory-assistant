import json
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Medicine, DoseLog

router    = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _generate_today_doses(db: Session, medicine: Medicine):
    today = date.today()
    times = json.loads(medicine.intake_times)
    for t in times:
        h, m = map(int, t.split(":"))
        scheduled = datetime.combine(today, datetime.min.time().replace(hour=h, minute=m))
        exists = db.query(DoseLog).filter_by(
            medicine_id=medicine.id, scheduled_dt=scheduled).first()
        if not exists:
            db.add(DoseLog(
                medicine_id=medicine.id,
                user_id=medicine.user_id,
                scheduled_dt=scheduled,
                status="pending"
            ))


@router.get("/medicines", response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
    user: User  = Depends(get_current_user)
):
    medicines = db.query(Medicine).filter_by(
        user_id=user.id, is_active=True
    ).order_by(Medicine.name).all()

    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end   = datetime.combine(date.today(), datetime.max.time())
    today_doses = db.query(DoseLog).filter(
        DoseLog.user_id == user.id,
        DoseLog.scheduled_dt.between(today_start, today_end)
    ).order_by(DoseLog.scheduled_dt).all()

    return templates.TemplateResponse(request, "medicines.html", {
        "user": user,
        "medicines": medicines, "today_doses": today_doses
    })


@router.post("/medicines/add")
async def add(
    request: Request,
    db: Session = Depends(get_db),
    user: User  = Depends(get_current_user)
):
    form = await request.form()
    times = form.getlist("intake_times")
    times = [t.strip() for t in times if t.strip()]

    start = datetime.strptime(form.get("start_date"), "%Y-%m-%d").date()
    end_raw = form.get("end_date", "")
    end = datetime.strptime(end_raw, "%Y-%m-%d").date() if end_raw else None

    med = Medicine(
        user_id              = user.id,
        name                 = form.get("name", "").strip(),
        dosage               = form.get("dosage", "").strip(),
        frequency            = form.get("frequency", "once_daily"),
        intake_times         = json.dumps(times),
        start_date           = start,
        end_date             = end,
        with_food            = form.get("with_food", "either"),
        special_instructions = form.get("special_instructions", "").strip() or None,
        alert_on_miss        = form.get("alert_on_miss") == "on",
    )
    db.add(med)
    db.flush()
    _generate_today_doses(db, med)
    db.commit()
    return RedirectResponse(url="/medicines", status_code=302)


@router.post("/medicines/{med_id}/delete")
def delete(med_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    med = db.query(Medicine).filter_by(id=med_id, user_id=user.id).first()
    if med:
        med.is_active = False
        db.commit()
    return RedirectResponse(url="/medicines", status_code=302)


@router.post("/medicines/dose/{dose_id}/take")
def take_dose(dose_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    dose = db.query(DoseLog).filter_by(id=dose_id, user_id=user.id).first()
    if dose:
        dose.status  = "taken"
        dose.taken_at= datetime.utcnow()
        db.commit()
    return RedirectResponse(url="/medicines", status_code=302)