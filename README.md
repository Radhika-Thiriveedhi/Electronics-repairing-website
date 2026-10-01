# FixLoop — Repair, Reuse & Service Tracking Platform

FixLoop is a full-featured marketplace and service tracking platform that connects customers with local repair hubs, enables transparent quote comparison, facilitates technician progress tracking in real time, and promotes electronic sustainability through repair and reuse.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture & Design](#architecture--design)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Build](#build)
- [Run](#run)
- [Usage](#usage)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [License](#license)

---

## 🌟 Overview

Instead of discarding items when they break, FixLoop empowers a circular economy:
1. **Customer Portal**: Add items, report faults, select drop-off or doorstep pickup, review estimates, approve quotes, track status in real-time, and leave reviews.
2. **Repair Shop Dashboard**: Intake incoming requests, perform initial inspection, dispatch quotes, assign certified technicians, manage parts inventory, and track earnings.
3. **Technician Workbench**: Update stage progress (`Received` → `Diagnosing` → `Waiting for Approval` → `Repairing` → `Ready for Collection` → `Completed`), log diagnosis notes, and record spare parts used.
4. **Platform Owner Dashboard**: Central monitoring of registered shops, job volumes, platform GMV revenue, category statistics, and completion analytics via interactive Chart.js graphs.

---

## 🏛️ Architecture & Design

- **Backend Framework**: Python 3.11 with Flask application factory pattern (`app/__init__.py`).
- **Session Management**: Flask-Login session management with Werkzeug password hashing.
- **Persistence Layer**: Zero-database local JSON architecture using atomic replacement (`os.replace`) with file locking to ensure multi-threaded data consistency.
- **Frontend Layer**: Modular server-rendered Jinja2 HTML5 templates, modern responsive CSS design system, and client-side JavaScript for dynamic updates.

---

## 📦 Dependencies

FixLoop requires the following dependencies specified in `requirements.txt` and `pyproject.toml`:
- `Python >= 3.11`
- `Flask >= 3.0.0`
- `Flask-Login >= 0.6.3`
- `Flask-WTF >= 1.2.1`
- `email-validator >= 2.1.0`
- `pytest >= 8.0.0` (Development & Testing)

Dependency lockfiles provided:
- `poetry.lock`
- `package-lock.json`

---

## ⚙️ Installation

### 1. Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/FixLoop/FixLoop.git
cd FixLoop
```

### 2. Set up a Python Virtual Environment:
```bash
python -m venv .venv
```

Activate the virtual environment:
- **Windows (PowerShell)**:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt)**:
  ```cmd
  .\.venv\Scripts\activate.bat
  ```
- **macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

### 3. Install Required Dependencies:
```bash
pip install -r requirements.txt
```

Alternatively, install using `poetry`:
```bash
poetry install
```

Or install frontend/build scripts via `npm`:
```bash
npm install
```

---

## 🔨 Build

To validate application setup and compile local assets:

Using Makefile:
```bash
make build
```

Using npm scripts:
```bash
npm run build
```

Using Docker:
```bash
docker build -t fixloop:latest .
```

---

## 🚀 Run

You can launch the FixLoop platform using any of the following methods:

### Option A: Direct Python Entry Point
```bash
python main.py
```
Or:
```bash
python app.py
```
Or:
```bash
python run.py
```

### Option B: Using npm scripts
```bash
npm start
```

### Option C: Using Makefile
```bash
make run
```

### Option D: Using Docker Compose
```bash
docker-compose up --build
```

Access the application in your browser at:
👉 **http://127.0.0.1:5000**

---

## 📖 Usage

### Quick Demo Accounts
For rapid role testing, use the Quick Switch Demo Bar located at the top of the interface:
- **Customer**: `customer@fixloop.org` (Password: `password123`)
- **Repair Shop Owner**: `shop@fixloop.org` (Password: `password123`)
- **Technician**: `technician@fixloop.org` (Password: `password123`)
- **Platform Owner**: `owner@fixloop.org` (Password: `password123`)

### Real-World Service Journey Walkthrough
1. **Submit Request**: Log in as Customer and submit a repair ticket for "Laptop charging problem".
2. **Review & Accept**: Switch to Shop Owner, accept incoming ticket, and submit a quote of ₹800–₹1,200.
3. **Approve Quote**: Switch to Customer and click "Approve Quote".
4. **Repair Work**: Switch to Technician, set status to `Repairing`, add diagnosis notes, and record spare parts.
5. **Collection & Completion**: Move status to `Ready for Collection`. The customer processes payment, and the shop marks the job `Completed`.

---

## 🧪 Testing

Execute the automated test suite covering authentication, repair status state machines, quotes, access control permissions, and analytics:

```bash
pytest -v
```

Or using Makefile:
```bash
make test
```

Or using npm:
```bash
npm test
```

---

## 🐳 Docker Deployment

To build and run FixLoop as an isolated container:

```bash
# Build the Docker image
docker build -t fixloop .

# Run container exposing port 5000
docker run -p 5000:5000 --name fixloop-app fixloop
```

---

## 📄 License

This software is proprietary and confidential. All rights reserved. FixLoop Platform.
