# 👴👵 ElderCare Assistant

An AI-powered Elderly Care Management Web Application built using **FastAPI**, **SQLite**, **Jinja2**, and **Bootstrap**.

The system helps elderly people and caregivers manage medicines, appointments, health records, emergency alerts, and personal profiles through a simple and user-friendly interface.

---

## 🚀 Features

### 🔐 Authentication
- User Registration
- User Login
- Secure Password Hashing (bcrypt)
- Session-Based Authentication
- Logout Functionality

### 💊 Medicine Management
- Add Medicines
- Edit Medicines
- Delete Medicines
- Medicine Reminder Scheduling

### 📅 Appointment Management
- Create Appointments
- Update Appointments
- Delete Appointments
- Appointment Tracking

### ❤️ Health Logs
- Blood Pressure Tracking
- Sugar Level Monitoring
- Weight Records
- Health History Management

### 🚨 Emergency Alerts
- Emergency Contact Alerts
- Notification System
- Alert Management Dashboard

### 👤 User Profile
- Update Personal Information
- Manage Account Settings

### 🔌 API Endpoints
- Health Check API
- Future Mobile Integration Support

---

# 🛠️ Technology Stack

| Category | Technology |
|----------|-------------|
| Backend | FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Templates | Jinja2 |
| Authentication | Passlib (bcrypt) |
| Session Management | ItsDangerous |
| Scheduling | APScheduler |
| Email Services | FastAPI-Mail |
| Frontend | HTML, CSS, Bootstrap |
| Server | Uvicorn |

---

# 📂 Project Structure

```text
ElderCare_FastAPI/
│
├── .env
├── config.py
├── main.py
├── requirements.txt
│
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
│
├── app/
│
│   ├── auth.py
│   ├── database.py
│   ├── dependencies.py
│
│   ├── models/
│   │   ├── user.py
│   │   ├── medicine.py
│   │   ├── appointment.py
│   │   ├── health_log.py
│   │   └── alert.py
│
│   ├── routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── medicines.py
│   │   ├── appointments.py
│   │   ├── health_log.py
│   │   ├── alerts.py
│   │   ├── profile.py
│   │   └── api.py
│
│   ├── services/
│   │   └── scheduler.py
│
│   └── templates/
│       ├── auth/
│       ├── dashboard/
│       ├── medicines/
│       ├── appointments/
│       ├── health/
│       ├── alerts/
│       └── errors/
│
└── eldercare.db
```

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/ElderCare_FastAPI.git
cd ElderCare_FastAPI
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
```

---

## 3. Activate Virtual Environment

### CMD

```cmd
.venv\Scripts\activate
```

### PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Git Bash / Antigravity IDE

```bash
source .venv/Scripts/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔧 Environment Variables

Create a `.env` file:

```env
APP_ENV=development

SECRET_KEY=eldercare@2026

DATABASE_URL=sqlite:///./eldercare.db

MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@gmail.com

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_TLS=True
MAIL_SSL=False
```

---

# 🗄️ Database Setup

SQLite database is automatically created:

```bash
python main.py
```

---

# ▶️ Running the Application

```bash
python main.py
```

OR

```bash
uvicorn main:app --reload
```

---

# 🌐 Access the Application

## Home

```text
http://localhost:8000
```

---

## Login

```text
http://localhost:8000/login
```

---

## Register

```text
http://localhost:8000/register
```

---

## Swagger Documentation

```text
http://localhost:8000/docs
```

---

## ReDoc API Documentation

```text
http://localhost:8000/redoc
```

---

# 🧪 Testing Features

## Authentication
- Register New User
- Login
- Logout

---

## Medicines
- Add Medicine
- Edit Medicine
- Delete Medicine

---

## Appointments
- Create Appointment
- Update Appointment
- Delete Appointment

---

## Health Logs
- Add Blood Pressure
- Add Sugar Levels
- Add Weight Records

---

## Emergency Alerts
- Create Alerts
- View Notifications

---

## Profile
- Update User Information

---

# 🔐 Security Features

- Password Hashing using bcrypt
- Session-Based Authentication
- Secure Cookies
- CSRF Protection Ready
- Environment Variable Configuration

---

# 📌 Future Improvements

- AI Voice Assistant
- Medicine Reminder Notifications
- SMS Integration
- Caregiver Mobile App
- AI Health Monitoring
- Emergency SOS System
- Location Sharing
- Real-Time Video Calling

---

