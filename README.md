# RDRS — Real-Time Detection and Response System

RDRS is a security monitoring project designed to demonstrate file-event monitoring, security status reporting, alert and incident handling, and a web-based dashboard. It provides an API for interacting with monitoring data and supports simulation mode for controlled demonstrations.

**GitHub Repository:** https://github.com/saideshmukh-cyber/RDRS

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Configuration](#configuration)
- [Security Considerations](#security-considerations)
- [Limitations](#limitations)
- [Author](#author)

## Project Overview

RDRS demonstrates how a monitoring application can collect file-system events, expose security-related information through a REST API, and present monitoring results through a dashboard.

The application is built with Python and FastAPI and can be run using Docker Compose. It includes a simulation mode to support controlled testing and demonstrations without requiring a production security-monitoring environment.

## Features

- **File monitoring:** Detects and records file-system events in configured watch directories.
- **Security status:** Provides a status endpoint with the current monitoring score, severity level, event count, and monitored paths.
- **Event management:** Exposes recorded file events through the API.
- **Alert and incident endpoints:** Provides access to security alerts and incident information.
- **Process monitoring data:** Exposes process snapshot information through the API.
- **Web dashboard:** Provides a browser-based interface for viewing monitoring information.
- **Settings management:** Supports reading settings and making permitted configuration updates.
- **Reports:** Supports report access and export in supported formats, including JSON, CSV, HTML, and PDF.
- **Simulation mode:** Supports controlled demonstrations and testing.
- **Automated tests:** Includes a pytest test suite for checking application functionality and API behaviour.
- **Docker support:** Allows the application to run in a containerized environment.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| FastAPI | REST API |
| SQLAlchemy | Database interaction |
| SQLite | Local database storage |
| Docker | Application containerization |
| Docker Compose | Application startup and configuration |
| Pytest | Automated testing |
| HTML, CSS and JavaScript | Web dashboard |
| Watchdog | File-system event monitoring |

## Project Structure

The following is a high-level overview of the important project components.

```text
RDRS/
├── app/
│   ├── api/                 # API routes and application entry points
│   ├── core/                # Core configuration and application logic
│   └── detectors/           # Monitoring and detection components
├── tests/                   # Automated tests
├── data/                    # Local database and monitoring data
│   └── sandbox/             # Directory used for controlled demonstrations
├── logs/                    # Application logs
├── backups/                 # Local database backups
├── config.yaml              # Application configuration
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker image configuration
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

*Note: The exact files and directories may vary slightly depending on the project version.*

## Prerequisites

Before running RDRS, install:

- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose support
- A modern web browser

Python and a virtual environment are also useful if you want to run tests or work on the application outside Docker.

## Installation and Setup

### 1. Clone the repository

Open Git Bash or a terminal and run:

```bash
git clone https://github.com/saideshmukh-cyber/RDRS.git
cd RDRS
```

### 2. Check Docker

Make sure Docker Desktop is running, then execute:

```bash
docker --version
docker compose version
```

Both commands should display version information.

### 3. Start the application

From the project root directory, run:

```bash
docker compose up --build -d
```

This builds the application image if needed and starts the configured services in the background.

### 4. Verify the container

Run:

```bash
docker compose ps
```

To inspect the application logs:

```bash
docker compose logs -f rdrs
```

Press `Ctrl+C` to stop following the logs. This does not, by itself, stop the container.

## Running the Application

The current local Docker configuration maps host port **8001** to the application's container port.

Open these addresses in your browser:

| Resource | URL | Purpose |
|---|---|---|
| Dashboard | http://localhost:8001/dashboard | Web dashboard |
| Health check | http://localhost:8001/health | Application health |
| Monitoring status | http://localhost:8001/status | Current monitoring status |
| API documentation | http://localhost:8001/docs | Interactive API documentation, if enabled |

A successful health check should return a response similar to:

```json
{
  "status": "ok",
  "service": "rdrs"
}
```

The monitoring status response provides information such as the current score, severity level, event count, and monitored paths.

### Stop the application

To stop the services:

```bash
docker compose down
```

This stops and removes the Compose containers and network. It does not normally delete host-mounted application data.

To start the application again:

```bash
docker compose up -d
```

## API Endpoints

RDRS exposes API endpoints for monitoring, settings, events, alerts, incidents, process information, scanning, and reports.

The following table lists the main endpoint paths used by the project. Refer to the interactive API documentation at `/docs` for the precise methods, parameters, and response schemas implemented in the current version.

| Endpoint | Purpose |
|---|---|
| `/health` | Checks application health |
| `/status` | Retrieves monitoring status |
| `/events` | Accesses recorded file events |
| `/alerts` | Accesses security alerts |
| `/incidents` | Accesses incident information |
| `/processes` | Accesses process monitoring data |
| `/settings` | Reads or updates permitted settings |
| `/scan` | Invokes the scanning functionality |
| `/reports` | Accesses report functionality |
| `/dashboard` | Opens the web dashboard |

For local testing, use the base URL:

```text
http://localhost:8001
```

## Testing

RDRS includes automated tests covering application and API behaviour.

### Run the test suite

If the Python dependencies are installed in the active environment, execute this command from the project root:

```bash
python -m pytest -q
```

The latest recorded test run completed with **49 passed tests and 1 warning**. Results may differ if the project code, environment, or dependencies change.

To run a specific test file:

```bash
python -m pytest tests/test_api_smoke.py -v
```

To check for whitespace errors in Git changes:

```bash
git diff --check
```

## Configuration

Application settings are managed through the project configuration and environment variables.

The current setup includes:

- `config.yaml` for application configuration.
- `RDRS_HOST` and `RDRS_PORT` for the server binding inside the container.
- `RDRS_SIMULATION_MODE` to control simulation mode.
- `RDRS_DATABASE_URL` to configure the database connection.

The default database configuration uses SQLite at:

```text
sqlite:///./data/rdrs.db
```

The Docker configuration mounts local data and log directories into the container so that application data can persist outside the container.

Review `config.yaml`, `app/core/config.py`, `Dockerfile`, and `docker-compose.yml` before changing configuration values. Keep passwords, API keys, and other secrets out of source control.

## Security Considerations

RDRS is intended as a development, demonstration, and educational project unless it has been separately hardened and validated for production use.

- **Authentication and authorization:** The current version does not have API authentication or authorization. Do not expose it directly to the public internet in this configuration.
- **Simulation mode:** Use simulation mode for controlled demonstrations and testing.
- **Monitoring scope:** File monitoring is limited to the directories configured and accessible to the application.
- **Container isolation:** Running RDRS in Docker does not automatically grant it visibility into every file on the host computer.
- **Data protection:** Back up important databases and review what data is collected before using the system with real files.
- **Deployment:** A hosted container generally monitors the files accessible inside that hosted environment, not the files on your personal Windows computer.

Before any public deployment, implement and test appropriate authentication, authorization, secure configuration, logging, and network access restrictions.

## Limitations

- Monitoring is limited to configured watch paths and the runtime environment's filesystem access.
- Detection and status results depend on the available event data and implemented detection logic.
- Simulation mode is designed for demonstrations and should not be interpreted as proof of production-grade threat detection.
- The project has not been represented here as independently audited or production-certified.
- A successful automated test suite does not guarantee that every deployment environment or security scenario will behave identically.

## Author

**Sai Deshmukh**

GitHub: https://github.com/saideshmukh-cyber

## Project Status

RDRS has a Docker-based local run configuration and an automated test suite. The repository is available on GitHub.

A public live deployment is not specified in this README. If a live demonstration URL is required for submission, add the verified URL here after deployment and security checks.
