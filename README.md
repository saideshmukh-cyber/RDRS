# RDRS — Ransomware Detection and Response System

Educational defensive monitor for ransomware-like file activity. This is a student/demo project, **not a production endpoint detection and response (EDR) product**. It does not encrypt files, execute malware, or kill processes. Keep simulation mode enabled and test only inside `data/sandbox`.

## Included functionality

- Watchdog filesystem monitoring for create/modify/delete/rename events
- Shannon entropy sampling and rule-based sliding-window scoring
- Process snapshots using `psutil`
- SQLite persistence for events, alerts, incidents, and process snapshots
- Critical incident creation and evidence-copy quarantine (originals are not moved/deleted by the responder)
- FastAPI API and Swagger UI
- Browser dashboard with CSS/JS served from dedicated routes
- JSON, CSV, HTML and PDF incident reports
- Pytest unit/integration/API smoke tests
- Dockerfile and Compose deployment
- GitHub Actions test workflow

## Requirements

- Python 3.12+
- Git Bash or PowerShell on Windows
- Docker Desktop for container deployment (optional)

## Install and run (Windows Git Bash)

Run from the repository root (`RDRS/`):

```bash
python --version
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python -m pytest -q
python -m app.main --host 127.0.0.1 --port 8001
```

Open `http://127.0.0.1:8001/`, API docs at `/docs`, health at `/health`, status at `/status`. Keep the `.env` file local; never commit it. The default config watches only `data/sandbox`.

## Test and coverage

```bash
python -m compileall -q app tests scripts
python -m pytest -q
python -m pytest --cov=app --cov-report=term-missing
```

## Safe simulation

Back up any wanted content in `data/sandbox` first. The simulator deletes existing top-level `.txt` and `.locked` files in that sandbox before creating disposable samples. Start RDRS in terminal 1, then from terminal 2 (same project root and venv) run:

```bash
python scripts/simulate_attack.py
```

Verify score/signals, alerts, incidents and evidence copies—not just filesystem event capture. Do not run on real files or widen watched paths for a demo.

## Docker Compose

Container port is 8000 and host port is 8001 (`8001:8000`). With Docker Desktop running:

```bash
docker compose config
docker compose build --no-cache
docker compose up -d
docker compose ps
docker compose logs --tail=200 rdrs
```

Visit `http://127.0.0.1:8001/`, `/docs`, `/health`. Stop with `docker compose down`; don't add `-v` if preserving data matters.

## Reports

Get a real incident ID from `/incidents`, then replace `INCIDENT_ID` below:

```bash
curl -OJ http://127.0.0.1:8001/reports/INCIDENT_ID/json
curl -OJ http://127.0.0.1:8001/reports/INCIDENT_ID/csv
curl -OJ http://127.0.0.1:8001/reports/INCIDENT_ID/html
curl -OJ http://127.0.0.1:8001/reports/INCIDENT_ID/pdf
```

## GitHub

Review `git status --short`, `git diff --check`, and staged files before committing. `.env`, `.venv`, databases, logs, sandbox files, quarantine evidence and generated reports must not be committed. If already cloned, inspect `git remote -v` and do not reinitialize Git.

## Security / deployment boundary

The API currently has no authentication. This release is for local demonstration or isolated evaluation only; do not expose it publicly as-is. Public/production deployment requires authentication/authorization, TLS, restrictive CORS, rate limiting, secret management, audit logging, backup/recovery, and operational monitoring. See `docs/RELEASE_CHECKLIST.md` for the full procedure.

## PRD traceability

A standalone PRD/FSD was not present in the ZIP audited here. Maintain requirement-to-code-to-test evidence against the actual PRD before claiming full compliance.

## FSD compliance and known limitations

See [docs/PRD_TRACEABILITY.md](docs/PRD_TRACEABILITY.md) for the requirement-by-requirement matrix based on FSD v1.0, acceptance evidence, and known gaps. Do not claim full compliance until the acceptance checklist passes on the target machine. In particular, unknown-program scoring is not implemented in this version, score history has no separate table, `/scan` reports current status rather than scanning an arbitrary path, and `/settings` changes only the runtime simulation flag. The API is unauthenticated and must not be exposed publicly as-is.
