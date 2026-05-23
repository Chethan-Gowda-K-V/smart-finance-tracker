# Antigravity Smart Expense & Finance Tracker

A premium, futuristic AI-powered Smart Expense & Finance Tracker web application built using **Django**, **Django REST Framework (DRF)**, **Supabase PostgreSQL** (or local SQLite), and deployed on **Render**.

This project features a cinematic glassmorphism UI/UX design with smooth transitions, interactive ApexCharts, dynamic statistics counters, and premium micro-interactions inspired by top fintech products.

---

## Key Features

1. **User Authentication**: Secure Login/Signup/Logout system with custom user models, monthly income targets, and profile setups.
2. **Expense Ledger & Scanning**:
   - **OCR Receipt Scanner**: Client-side scanning via `Tesseract.js` that parses total amounts and invoice descriptions instantly.
   - **AI Voice Expense Entry**: Speech-to-text transcription parsing powered by the **Google Gemini API** (falls back to offline regex parsers).
   - Dynamic search, filters (daily, weekly, monthly), and multi-account ledgers.
3. **Budgets & Goals Planner**:
   - Set monthly budget boundaries per category.
   - Set savings milestones goals with progress rings and an active "Add Funds" portal.
4. **AI Financial Assistant**:
   - Floating full-screen AI chatbot with custom typing indicators and suggestions quick chips.
   - Personalized financial insights, next-month expense predictions, and budget warnings.
5. **Real-time Notifications**: Custom budget limit warnings (80% and 100% threshold checks) and savings goal completion alerts.
6. **Executive Reports**:
   - Download professional PDF statement summaries generated with `reportlab`.
   - Download Excel ledger worksheets styled and formatted with `openpyxl`.
7. **Savings Challenge Gamification**: Unlock achievement badges (First Saver, Speech Command, OCR Scanner) with interactive 3D hover tilt effects and canvas confetti triggers.

---

## Tech Stack

- **Backend**: Django 4.2+, Django REST Framework (DRF), SimpleJWT
- **Database**: Supabase PostgreSQL (via `dj-database-url` and `psycopg2-binary`) or local SQLite
- **AI Engine**: Google Generative AI (Gemini 1.5 Flash)
- **Frontend**: HTML5, CSS3, Tailwind CSS, Bootstrap Icons, GSAP, Canvas Plexus Particles, ApexCharts, Tesseract.js, Web Speech API

---

## Installation & Local Setup

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Clone and Prepare Environment
```bash
# Navigate to the workspace folder
cd "smart exp and finc traker"

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (based on `.env.example`):
```env
SECRET_KEY=django-insecure-smart-finance-tracker-dev-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com

# For Supabase PostgreSQL, set the DATABASE_URL. If blank, local SQLite is used automatically.
DATABASE_URL=

# Google Gemini API key for Chatbot, OCR, and AI Insights
GEMINI_API_KEY=your-gemini-api-key-here
```

### 5. Run Migrations & Create Admin Superuser
```bash
# Apply database schemas
python manage.py migrate

# Create an administrator to access /admin/
python manage.py createsuperuser
```

### 6. Run Server
```bash
python manage.py runserver
```
Visit the application in your browser at `http://127.0.0.1:8000/`.

---

## Folder Structure

```
├── smart_finance/          # Django global core (settings.py, urls.py, wsgi.py)
├── authentication/         # JWT Auth, Custom User model, login/signup forms & views
├── expenses/               # Core Accounts, Categories, Transactions, Budgets, Savings models
├── ai_assistant/           # Gemini Chatbot, Speech Parser, AI Insights endpoints
├── notifications/          # Real-time budget warning toasts and notification logs
├── reports/                # PDF statements (ReportLab) and Excel sheets (OpenPyXL)
├── templates/              # Global HTML templates (base.html, dashboard, ledger, etc.)
├── static/                 # Custom main.css styling and images
├── manage.py               # Django execution CLI
└── render.yaml             # Render infrastructure deployment config
```

---

## Deployment on Render

This project is fully ready for deployment on **Render** via the provided `render.yaml` configuration.

1. Create a new Web Service on Render linked to your repository.
2. Render will automatically parse the `render.yaml` config and provision the service.
3. Configure the environment variables `DATABASE_URL` (from Supabase) and `GEMINI_API_KEY` (from Google AI Studio) in the Render dashboard.
4. The backend build commands are automated in `build.sh` (collectstatic + migrations).
