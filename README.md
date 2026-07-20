# 🚀 HireFlow – Full-Stack Job Portal & Recruitment Management Platform

[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0.6-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-27%20Passed-success)](https://github.com/)

**HireFlow** is a feature-packed, production-ready recruitment web application built with Python and Django. Designed with modern user experience principles and robust Role-Based Access Control (RBAC), HireFlow connects job seekers (Candidates) and hiring managers (Recruiters) in a streamlined recruitment workflow.

---

## ✨ Key Features

### 👤 Dual Authentication & User Profiles
- **Role-Based Registration & Login**: Custom user model distinguishing between Candidates and Recruiters.
- **Profile Customization**: Candidates can upload resumes, manage bios, phone numbers, and professional details.
- **Email & Username Authentication**: Flexible authentication backend allowing login via either email or username.

### 🏢 Recruiter & Company Management
- **Company Profile CRUD**: Recruiters can register company profiles complete with logo upload, website, location, and description.
- **Job Posting Lifecycle**: Full Create, Read, Update, Delete (CRUD) operations for job listings with job type (Full-time, Part-time, Contract, Internship) and workplace mode (Remote, Hybrid, On-site).
- **Application Status Lifecycle**: Recruiters can review submitted applications and update statuses (`Pending`, `Reviewing`, `Interviewing`, `Shortlisted`, `Rejected`, `Hired`) with instant status badges.

### 💼 Candidate Job Discovery & Application Flow
- **Advanced Job Search & Filtering**: Multi-criteria search by keyword, job type, workplace model, and location.
- **One-Click Job Application**: Candidates can apply with one click using their profile resume or upload a custom resume per application.
- **Job Bookmarking / Saved Jobs**: Candidate toggle to save/unsave jobs for later review.
- **Interactive Candidate Dashboard**: Real-time overview of active applications, application statuses, and saved jobs.

### ✉️ Contact System & Feedback
- **Contact Form**: Interactive user contact submission with database storage and admin view tracking.

### 🔒 Security & RBAC
- Strict permission checks preventing non-owners or non-recruiters from editing company details or modifying job listings.
- CSRF protection, password validation, and secure session management.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Backend Framework** | [Django 6.0](https://www.djangoproject.com/) |
| **Programming Language** | [Python 3.14+](https://www.python.org/) |
| **Database** | SQLite (Dev) / PostgreSQL (Production) via `dj-database-url` |
| **Static File Handling** | [WhiteNoise](https://whitenoise.readthedocs.io/) |
| **WSGI Server** | [Gunicorn](https://gunicorn.org/) |
| **Frontend** | HTML5, Vanilla CSS3, Modern UI Components |
| **Testing** | Django Test Suite (27 Unit & Integration Tests) |

---

## 📁 Project Architecture

```
HireFlow/
├── accounts/          # User authentication, custom user model, profiles & dashboards
├── companies/         # Recruiter company profile management & public directory
├── jobs/              # Job creation, listing, search, filtering & application tracking
├── contact/           # User inquiry submissions & contact form handling
├── home/              # Homepage, about page, and error handlers (404, 403)
├── hireflow/          # Main project configuration (settings.py, urls.py, wsgi.py)
├── static/            # CSS, JavaScript, logo assets, and UI components
├── staticfiles/       # Production gathered static assets (collected via collectstatic)
├── media/             # Local upload storage for resumes & company logos
├── .env.example       # Template for required environment variables
├── build.sh           # Automated build script for deployment platforms
├── Procfile           # Production Gunicorn execution specification
└── render.yaml        # Infrastructure as Code for Render deployment
```

---

## ⚙️ Local Development Setup

Follow these steps to run HireFlow locally:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/HireFlow.git
cd HireFlow
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 5. Apply Database Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Run Test Suite
```bash
python manage.py test accounts.tests companies.tests contact.tests jobs.tests
```

### 8. Start Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your web browser.

---

## ☁️ Production Deployment Guide (Render / Railway)

HireFlow comes pre-configured with `WhiteNoise`, `dj-database-url`, `Procfile`, and `build.sh` for easy one-click cloud deployment.

### Deploying to Render:
1. Push your repository to **GitHub**.
2. Log into [Render](https://render.com/) and click **New +** > **Web Service**.
3. Connect your GitHub repository.
4. Select **Python** runtime environment.
5. Set Build Command: `./build.sh`
6. Set Start Command: `gunicorn hireflow.wsgi:application`
7. Add Environment Variables:
   - `SECRET_KEY`: *(Generate a secure random key)*
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.onrender.com`
8. Click **Deploy Web Service**!

---

## 🧪 Automated Testing

HireFlow maintains high test coverage ensuring security and application reliability. All 27 tests pass cleanly across user authentication, company CRUD, job application lifecycles, and RBAC permissions.

To execute the test suite:
```bash
python manage.py test accounts.tests companies.tests contact.tests jobs.tests
```

---

## 🔮 Future Roadmap & Enhancements

- [ ] **Email Notifications**: Send transactional email alerts upon job application status changes.
- [ ] **Cloud Storage**: AWS S3 integration for persistent media storage.
- [ ] **Containerization**: Docker & Docker Compose setup for standardized deployment environments.
- [ ] **CI/CD Integration**: GitHub Actions workflow for automated test execution on pull requests.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.