# RDRS — Ransomware Detection and Response System

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-50%20passed-success)](#testing)

RDRS is a Python-based security monitoring and demonstration project. It collects file-system activity from configured watch directories, records process snapshots, evaluates activity using detection and scoring logic, and presents security information through a web dashboard and REST API.

**Live application:** [https://ransomware-detectionandresponse-system.onrender.com/](https://ransomware-detectionandresponse-system.onrender.com/)

**GitHub repository:** [https://github.com/saideshmukh-cyber/RDRS](https://github.com/saideshmukh-cyber/RDRS)

> **Project scope:** RDRS is an educational and demonstration system, not a substitute for a fully audited endpoint detection and response (EDR) product. Its hosted Render instance monitors only the filesystem available inside its own container. It does not monitor files or processes on a visitor's personal computer.

---

## Table of Contents

- [Features](#features)
- [Architecture and Technology](#architecture-and-technology)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Run Locally with Docker](#run-locally-with-docker)
- [Run Locally with Python](#run-locally-with-python)
- [Configuration](#configuration)
- [Admin Authentication](#admin-authentication)
- [Database](#database)
- [Dashboard and API](#dashboard-and-api)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security Considerations](#security-considerations)
- [Limitations](#limitations)
- [Troubleshooting](#troubleshooting)
- [Author](#author)

---

## Features

- **File-System Monitoring:** Monitors configured directories and records supported file-system events.
- **Ransomware Behaviour Detection:** Evaluates file activity using configurable detection thresholds and scoring rules.
- **Threat Scoring:** Calculates security scores based on observed activity.
- **Alert Management:** Records and displays generated security alerts.
- **Incident Management:** Stores incident information for investigation.
- **Process Monitoring:** Collects process snapshots from the environment in which RDRS runs.
- **Security Dashboard:** Provides a browser-based interface for monitoring application status and security information.
- **Admin Authentication:** Protects operational dashboard APIs using session-based authentication.
- **REST API:** Provides endpoints for monitoring status, events, alerts, incidents, processes, settings, scans, and reports.
- **Report Generation:** Supports JSON, CSV, HTML, and PDF report formats.
- **Simulation Mode:** Supports controlled demonstrations and testing.
- **Database Support:** SQLite for local development and PostgreSQL for hosted deployment.
- **Docker Support:** Includes Dockerfile and Docker Compose configuration.
- **Automated Testing:** Includes pytest tests for API endpoints, detection, monitoring, runtime, and repository functionality.

## Architecture and Technology

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| Backend Framework | FastAPI |
| Application Server | Uvicorn |
| ORM | SQLAlchemy |
| Local Database | SQLite |
| Hosted Database | PostgreSQL (Neon) |
| PostgreSQL Driver | Psycopg 3 |
| File-System Monitoring | Watchdog |
| Process Monitoring | psutil |
| Configuration | YAML and environment variables |
| Frontend | HTML, CSS, JavaScript |
| Containerization | Docker and Docker Compose |
| Testing | pytest |
| Hosting | Render |

## Project Structure

```text
RDRS/
│
├── app/
│   ├── api/                 # API routes and authentication
│   ├── core/                # Configuration and shared application logic
│   ├── dashboard/           # Dashboard pages and static assets
│   ├── database/            # Database engine and repository
│   ├── detectors/           # Detection and monitoring modules
│   └── reports/             # Report generation
│
├── tests/                   # Automated test suite
│
├── data/
│   ├── sandbox/             # Controlled monitoring directory
│   ├── quarantine/          # Local quarantine directory
│   └── reports/             # Generated reports
│
├── logs/                    # Application logs
│
├── config.yaml              # Application configuration
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker build instructions
├── requirements.txt         # Python dependencies
└── README.md
```

Runtime directories may be created automatically. Local databases, logs, backups, and secret files should not be committed to GitHub.

---

## Getting Started

### Prerequisites

Install the following:

- Python 3.12
- Git
- Docker Desktop
- A modern web browser

Clone the repository:

```bash
git clone https://github.com/saideshmukh-cyber/RDRS.git
cd RDRS
```

## Run Locally with Docker

Docker is the recommended way to run RDRS locally.

### 1. Create the environment file

Create a file named `.env` in the project root.

Add your local development configuration:

```dotenv
RDRS_ENV=development
RDRS_HOST=0.0.0.0
RDRS_PORT=8000
RDRS_SIMULATION_MODE=true
RDRS_DATABASE_URL=sqlite:///./data/rdrs.db

RDRS_ADMIN_USERNAME=admin
RDRS_ADMIN_PASSWORD_HASH=YOUR_ARGON2_PASSWORD_HASH
RDRS_SESSION_SECRET=YOUR_RANDOM_SESSION_SECRET
```

Replace the placeholders with your own generated credentials.

**Important:** Never upload `.env` to GitHub.

### 2. Build and start RDRS

Make sure Docker Desktop is running.

Execute:

```bash
docker compose up --build -d
```

### 3. Access the application

| Component | URL |
|---|---|
| Admin Login | http://localhost:8001/login |
| Dashboard | http://localhost:8001/dashboard |
| Health Check | http://localhost:8001/health |

Log in using your configured admin username and the original password used to generate the password hash.

Do not enter the password hash into the login form.

### 4. Useful Docker commands

Check container status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f rdrs
```

Stop the application:

```bash
docker compose down
```

Start the application again:

```bash
docker compose up -d
```

Stopping Docker Compose does not normally delete host-mounted database and log directories. Preserve your database and backups.

---

## Run Locally with Python

If you prefer not to use Docker, you can run the application directly.

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it using Git Bash:

```bash
source .venv/Scripts/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure `.env`

Create the `.env` file and configure the required database and authentication variables as described above.

### 4. Start the application

```bash
python -m app.main
```

Open:

http://127.0.0.1:8000/login

---

## Configuration

RDRS uses `config.yaml` and environment variables.

Important environment variables:

| Variable | Description |
|---|---|
| `RDRS_ENV` | Application environment |
| `RDRS_HOST` | Application host |
| `RDRS_PORT` | Local application port |
| `RDRS_DATABASE_URL` | Database connection URL |
| `RDRS_SIMULATION_MODE` | Enables or disables simulation mode |
| `RDRS_ADMIN_USERNAME` | Administrator username |
| `RDRS_ADMIN_PASSWORD_HASH` | Argon2 password hash |
| `RDRS_SESSION_SECRET` | Secret used for session signing |
| `RDRS_QUARANTINE_ENABLED` | Environment override for quarantine behaviour |
| `RDRS_ALLOW_ORIGINS` | Allowed application origins |

The default local database is:

```text
sqlite:///./data/rdrs.db
```

For hosted deployment, PostgreSQL can be configured through `RDRS_DATABASE_URL`.

Monitoring paths, thresholds, scoring rules, response settings, and report settings are configured in `config.yaml`.

Review configuration carefully before changing monitoring or response behaviour.

---

## Admin Authentication

RDRS uses password hashing rather than storing administrator passwords in plaintext.

Generate an Argon2 password hash using:

```bash
python -c "from getpass import getpass; from pwdlib import PasswordHash; password = getpass('New admin password: '); print(PasswordHash.recommended().hash(password))"
```

The generated hash should be configured in:

```text
RDRS_ADMIN_PASSWORD_HASH
```

Configure the corresponding username in:

```text
RDRS_ADMIN_USERNAME
```

Generate a secure session secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Configure it in:

```text
RDRS_SESSION_SECRET
```

**Important security notes:**

- Store your original password securely.
- Password hashes cannot be decoded to recover the original password.
- If you forget your password, generate a new password and hash, update the environment variable, and restart or redeploy.
- Never commit passwords, password hashes intended for private deployment, or session secrets.

---

## Database

RDRS supports two database options:

### SQLite

Used for local development and testing.

### PostgreSQL

Used for hosted deployments through Neon PostgreSQL.

The project includes the Psycopg 3 driver and automatically normalizes standard PostgreSQL connection URLs for SQLAlchemy.

The application creates missing database tables at startup.

Database backups should be maintained before database maintenance or schema changes. Automatic table creation is not a replacement for a formal database migration strategy.

---

## Dashboard and API

### Live Application

**[Open RDRS Security Dashboard](https://ransomware-detectionandresponse-system.onrender.com/)**

The application root redirects visitors to the administrator login page.

### Application Routes

| Endpoint | Purpose |
|---|---|
| `/` | Application entry point |
| `/login` | Administrator login |
| `/dashboard` | Security dashboard |
| `/health` | Health check |
| `/status` | Monitoring status |
| `/events` | File-system events |
| `/alerts` | Security alerts |
| `/incidents` | Security incidents |
| `/processes` | Process snapshots |
| `/settings` | Application settings |
| `/scan` | Detector and scan status |
| `/reports` | Report information and operations |
| `/auth/login` | Authentication endpoint |
| `/auth/logout` | Logout endpoint |

Operational API routes require an authenticated session.

The exact HTTP methods, request parameters, and response formats are defined in the application source code.

API documentation is disabled in the hosted configuration.

---

## Testing

RDRS uses pytest for automated testing.

Run the complete test suite:

```bash
python -m pytest -v
```

The latest verified test run during preparation of this documentation completed with:

```text
50 passed, 1 warning
```

The warning concerned a Starlette/httpx test-client deprecation notice. All tests passed.

Run an individual test module:

```bash
python -m pytest tests/test_api_smoke.py -v
```

Check Git changes for whitespace errors:

```bash
git diff --check
```

Test results may change as the application is updated.

---

## Deployment

The RDRS demonstration application is hosted on Render and uses Neon PostgreSQL.

### Live Deployment

**Application:** [https://ransomware-detectionandresponse-system.onrender.com/](https://ransomware-detectionandresponse-system.onrender.com/)

### Deployment Architecture

| Component | Platform |
|---|---|
| Application Hosting | Render |
| Container Runtime | Docker |
| Database | Neon PostgreSQL |
| Source Control | GitHub |
| Application Framework | FastAPI |

### Deployment Overview

1. Push application changes to the GitHub `main` branch.
2. Connect the GitHub repository to Render.
3. Create a Render Web Service using Docker.
4. Configure production environment variables.
5. Connect the Neon PostgreSQL database.
6. Configure administrator authentication.
7. Deploy the application.
8. Verify the health endpoint, database connection, and administrator login.

For the initial hosted demonstration, quarantine is disabled to avoid treating an ephemeral hosted filesystem as durable storage.

### Hosted-Service Considerations

Render's free service may spin down when inactive, and its local filesystem is ephemeral.

Neon provides database persistence, but files written only inside the Render container should not be considered durable.

The hosted application monitors only the environment and paths available inside its own container. It does not monitor the user's Windows computer or other external endpoints.

---

## Security Considerations

- Never commit `.env` files, database files, backups, private keys, or session secrets.
- Use strong and unique production administrator credentials.
- Use HTTPS for public access.
- Keep session secrets private.
- Keep simulation mode enabled for demonstrations unless real monitoring behaviour has been reviewed.
- Quarantine is a potentially destructive response action. Test it only in controlled environments with disposable sample files and verified backups.
- Restrict monitoring to directories you own or are authorized to monitor.
- Review application logs and alerts regularly.
- Back up important database information.
- A passing test suite does not constitute a security audit or penetration test.

## Limitations

RDRS is an educational security-monitoring project and has the following limitations:

1. Monitoring is restricted to configured watch paths.
2. Process visibility depends on operating-system permissions and container isolation.
3. Hosted Render monitoring is limited to the Render container.
4. The hosted application cannot independently monitor a visitor's personal computer.
5. Render's free filesystem is ephemeral.
6. Detection rules and scores cannot guarantee detection of every ransomware attack.
7. The current project has not been presented as a formally audited commercial EDR product.

For real endpoint monitoring, a separately installed and secured endpoint agent or deployment on the machine/network being monitored would be required.

---

## Troubleshooting

### Invalid username or password

- Verify `RDRS_ADMIN_USERNAME`.
- Enter the original password, not the Argon2 hash.
- If the password is forgotten, generate a new password and hash, update the configured hash, and restart or redeploy.

### Application fails to start

- Check application logs.
- Verify required authentication environment variables.
- Confirm the production database URL points to PostgreSQL rather than local SQLite.

### Dashboard shows no events

- Verify configured monitoring paths.
- Confirm the application has permission to access those paths.
- Remember that hosted monitoring sees only the container filesystem.

### Docker fails to start

Check Docker Desktop is running.

Validate the Compose configuration:

```bash
docker compose config --quiet
```

Inspect application logs:

```bash
docker compose logs -f rdrs
```

---

## Author

**Sai Deshmukh**

- GitHub: [@saideshmukh-cyber](https://github.com/saideshmukh-cyber)
- Repository: [RDRS](https://github.com/saideshmukh-cyber/RDRS)
- Live Application: [RDRS on Render](https://ransomware-detectionandresponse-system.onrender.com/)

---

*RDRS is an educational security-monitoring project. Use it only on systems and directories you own or are explicitly authorized to monitor.*
