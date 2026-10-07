# JanSetu (जनसेतु)

> **AI-Powered Citizen-Government-Academia Innovation & Problem Solving Platform**

JanSetu bridges citizens, government departments, academic institutions, and industry partners to identify, validate, solve, and track real-world public infrastructure and societal challenges through structured collaboration and AI-driven intelligence.

---

## 🌟 Architecture Overview

```
jansetu/
├── src/                     # React + Vite Frontend
│   ├── api/                 # API client & endpoint definitions
│   ├── components/          # Reusable UI components & screen views
│   ├── context/             # Authentication & JanSetu application state
│   ├── hooks/               # Custom React hooks (AI, challenges, government queue, etc.)
│   └── services/            # Frontend service layer
├── jansetu-backend/         # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/          # Modular API routers (auth, challenges, projects, etc.)
│   │   ├── core/            # Config, DB engine, security, exception handling
│   │   ├── models/          # SQLAlchemy ORM models
│   │   └── schemas/         # Pydantic v2 validation schemas
│   ├── alembic/             # Database migrations
│   └── tests/               # Test suites
├── start.bat                # Windows 1-click launcher (Cmd)
└── start.ps1                # PowerShell launcher
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js**: v18+ and `npm`
- **Python**: v3.11+
- **Git**

### 1. Automated Launcher (Windows)
Run either launcher script in the project root:
```powershell
.\start.ps1
```
or double-click `start.bat`.

### 2. Manual Setup

#### Backend Setup
```bash
cd jansetu-backend

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run backend server
python run.py
```
Backend runs at `http://localhost:8000` (Swagger docs: `http://localhost:8000/docs`).

#### Frontend Setup
```bash
# In the repository root
npm install

# Configure environment variables (optional for default localhost)
cp .env.example .env

# Start Vite development server
npm run dev
```
Frontend runs at `http://localhost:3000` (or `http://localhost:5173` if 3000 is occupied).

---

## 🛡️ Key Features

- **Citizen Problem Reporting**: Geo-tagged issue submission with multimedia attachment support.
- **AI Intelligence & Deduplication**: Automated duplicate detection, severity scoring, and category classification.
- **Government Action Workflow**: Departmental assignment, verification pipeline, and resolution tracking.
- **University Matching**: Connect complex civic problems to university research labs and student hackathons.
- **Industry & CSR Collaboration**: Public-private sponsorship, funding allocation, and CSR impact measurement.
- **Transparent Lifecycle & Impact Dashboard**: Live metrics and real-time status updates for all stakeholders.

---

## 📄 License
MIT License
