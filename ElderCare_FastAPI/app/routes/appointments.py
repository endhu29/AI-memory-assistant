from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Appointment
from app.services.notification import notify_appointment_reminder

router    = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/appointments", response_class=HTMLResponse)
def index(
    request: Request,
    status: str   = "all",
    db: Session   = Depends(get_db),
    user: User    = Depends(get_current_user)
):
    query = db.query(Appointment).filter_by(user_id=user.id)
    if status != "all":
        query = query.filter_by(status=status)
    appointments = query.order_by(Appointment.appointment_dt.desc()).all()
    return templates.TemplateResponse(request, "appointments.html", {
        "user": user,
        "appointments": appointments, "status_filter": status
    })


@router.post("/appointments/add")
def add(
    request: Request,
    doctor_name:         str  = Form(...),
    speciality:          str  = Form(""),
    appointment_date:    str  = Form(...),
    appointment_time:    str  = Form(...),
    hospital:            str  = Form(""),
    notes:               str  = Form(""),
    status:              str  = Form("Scheduled"),
    send_reminder_email: str  = Form(None),
    db: Session = Depends(get_db),
    user: User  = Depends(get_current_user)
):
    dt = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
    appt = Appointment(
        user_id             = user.id,
        doctor_name         = doctor_name.strip(),
        speciality          = speciality.strip() or None,
        appointment_dt      = dt,
        hospital            = hospital.strip() or None,
        notes               = notes.strip() or None,
        status              = status,
        send_reminder_email = send_reminder_email == "on",
    )
    db.add(appt)
    db.commit()
    return RedirectResponse(url="/appointments", status_code=302)


@router.post("/appointments/{appt_id}/edit")
def edit(
    appt_id: int,
    doctor_name:         str = Form(...),
    speciality:          str = Form(""),
    appointment_date:    str = Form(...),
    appointment_time:    str = Form(...),
    hospital:            str = Form(""),
    notes:               str = Form(""),
    status:              str = Form("Scheduled"),
    send_reminder_email: str = Form(None),
    db: Session = Depends(get_db),
    user: User  = Depends(get_current_user)
):
    appt = db.query(Appointment).filter_by(id=appt_id, user_id=user.id).first()
    if not appt:
        return RedirectResponse(url="/appointments", status_code=302)

    appt.doctor_name         = doctor_name.strip()
    appt.speciality          = speciality.strip() or None
    appt.appointment_dt      = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
    appt.hospital            = hospital.strip() or None
    appt.notes               = notes.strip() or None
    appt.status              = status
    appt.send_reminder_email = send_reminder_email == "on"
    db.commit()
    return RedirectResponse(url="/appointments", status_code=302)


@router.post("/appointments/{appt_id}/delete")
def delete(appt_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    appt = db.query(Appointment).filter_by(id=appt_id, user_id=user.id).first()
    if appt:
        appt.status = "Cancelled"
        db.commit()
    return RedirectResponse(url="/appointments", status_code=302)


@router.post("/appointments/{appt_id}/remind")
def remind(appt_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    appt = db.query(Appointment).filter_by(id=appt_id, user_id=user.id).first()
    if appt:
        notify_appointment_reminder(db, user, appt)
    return RedirectResponse(url="/appointments", status_code=302)