import json
from datetime import datetime, timedelta, date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

_scheduler = None


def start_scheduler(app_state):
    global _scheduler
    _scheduler = BackgroundScheduler(daemon=True)

    _scheduler.add_job(_check_missed_doses,    "interval", minutes=10,
                       id="check_missed_doses", replace_existing=True)
    _scheduler.add_job(_generate_daily_doses,  CronTrigger(hour=0, minute=5),
                       id="generate_daily_doses", replace_existing=True)
    _scheduler.add_job(_appointment_reminders, "interval", hours=1,
                       id="appointment_reminders", replace_existing=True)

    _scheduler.start()
    atexit.register(lambda: _scheduler.shutdown(wait=False))


def _get_db():
    from app.database import SessionLocal
    return SessionLocal()


def _check_missed_doses():
    db = _get_db()
    try:
        from app.models import DoseLog, User
        from app.services.notification import notify_medicine_missed
        cutoff  = datetime.utcnow() - timedelta(minutes=30)
        overdue = db.query(DoseLog).filter(
            DoseLog.status       == "pending",
            DoseLog.scheduled_dt <= cutoff,
            DoseLog.alert_sent   == False
        ).all()
        for dose in overdue:
            dose.status = "missed"
            if dose.medicine.alert_on_miss:
                user = db.query(User).get(dose.user_id)
                if user and user.profile:
                    notify_medicine_missed(
                        db, user, dose.medicine.name, dose.medicine.dosage,
                        dose.scheduled_dt.strftime("%d %b %Y %I:%M %p")
                    )
            dose.alert_sent = True
        db.commit()
    finally:
        db.close()


def _generate_daily_doses():
    db = _get_db()
    try:
        from app.models import Medicine, DoseLog
        today       = date.today()
        active_meds = db.query(Medicine).filter_by(is_active=True).all()
        for med in active_meds:
            if med.end_date and med.end_date < today:
                continue
            if med.start_date > today:
                continue
            times = json.loads(med.intake_times)
            for t in times:
                h, m = map(int, t.split(":"))
                scheduled = datetime.combine(today, datetime.min.time().replace(hour=h, minute=m))
                exists = db.query(DoseLog).filter_by(
                    medicine_id=med.id, scheduled_dt=scheduled).first()
                if not exists:
                    db.add(DoseLog(medicine_id=med.id, user_id=med.user_id,
                                   scheduled_dt=scheduled, status="pending"))
        db.commit()
    finally:
        db.close()


def _appointment_reminders():
    db = _get_db()
    try:
        from app.models import Appointment, User
        from app.services.notification import notify_appointment_reminder
        now    = datetime.utcnow()
        window = now + timedelta(hours=25)
        upcoming = db.query(Appointment).filter(
            Appointment.status             == "Scheduled",
            Appointment.send_reminder_email == True,
            Appointment.reminder_sent       == False,
            Appointment.appointment_dt.between(now, window)
        ).all()
        for appt in upcoming:
            user = db.query(User).get(appt.user_id)
            if user and user.profile:
                notify_appointment_reminder(db, user, appt)
            appt.reminder_sent = True
        db.commit()
    finally:
        db.close()