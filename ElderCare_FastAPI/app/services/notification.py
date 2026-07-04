import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from app.models import AlertLog
from config import get_settings

settings = get_settings()


def _send_smtp(to: str, subject: str, body: str) -> bool:
    try:
        msg = MIMEMultipart()
        msg["From"]    = settings.MAIL_FROM
        msg["To"]      = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            if settings.MAIL_TLS:
                server.starttls()
            if settings.MAIL_USERNAME:
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, to, msg.as_string())
        return True
    except Exception as e:
        print(f"[MAIL ERROR] {e}")
        return False


def send_email(db: Session, user_id: int, to: str, subject: str,
               body: str, alert_type: str, urgent: bool = False) -> bool:
    if urgent:
        subject = f"[URGENT] {subject}"

    ok    = _send_smtp(to, subject, body)
    log   = AlertLog(
        user_id       = user_id,
        alert_type    = alert_type,
        message       = body,
        sent_to_email = to,
        status        = "sent" if ok else "failed",
        error_detail  = None if ok else "SMTP failed",
    )
    db.add(log)
    db.commit()
    return ok


def notify_medicine_missed(db: Session, user, medicine_name: str,
                            dosage: str, scheduled_time: str) -> bool:
    if not user.profile or not user.profile.guardian_email:
        return False
    body = (
        f"Dear {user.profile.guardian_name},\n\n"
        f"{user.profile.full_name} missed their scheduled dose:\n"
        f"  Medicine : {medicine_name}\n"
        f"  Dosage   : {dosage}\n"
        f"  Scheduled: {scheduled_time}\n\n"
        f"Please check on them at your earliest convenience.\n\n"
        f"— ElderCare Assistant"
    )
    return send_email(db, user.id, user.profile.guardian_email,
                      "Medicine Dose Missed", body, "medicine_missed")


def notify_health_alert(db: Session, user, violations: list) -> bool:
    if not user.profile or not violations:
        return False
    lines = "\n".join(f"  • {v['metric']}: {v['value']} — {v['message']}" for v in violations)
    body  = (
        f"Dear {user.profile.guardian_name},\n\n"
        f"Health concern(s) detected for {user.profile.full_name}:\n\n"
        f"{lines}\n\n"
        f"Please review and consult a doctor if needed.\n\n"
        f"— ElderCare Assistant"
    )
    return send_email(db, user.id, user.profile.guardian_email,
                      "Health Alert — Readings Outside Safe Range", body,
                      "health_critical", urgent=True)


def notify_appointment_reminder(db: Session, user, appointment) -> bool:
    if not user.profile or not user.profile.guardian_email:
        return False
    dt_str = appointment.appointment_dt.strftime("%d %b %Y at %I:%M %p")
    body   = (
        f"Dear {user.profile.guardian_name},\n\n"
        f"Reminder: {user.profile.full_name} has a doctor appointment.\n\n"
        f"  Doctor    : Dr. {appointment.doctor_name}\n"
        f"  Speciality: {appointment.speciality or '—'}\n"
        f"  Date/Time : {dt_str}\n"
        f"  Hospital  : {appointment.hospital or '—'}\n\n"
        f"— ElderCare Assistant"
    )
    return send_email(db, user.id, user.profile.guardian_email,
                      f"Appointment Reminder — Dr. {appointment.doctor_name}",
                      body, "appointment_reminder") 