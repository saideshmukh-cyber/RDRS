# RDRS build, test, release and deployment checklist

> Scope: educational defensive monitoring demo. Do not expose this unauthenticated API to the public internet or monitor real/personal folders. Keep `data/sandbox` as the only watched path during development.

## 1. Environment

Use Python 3.12. From the repository root:

### Windows Git Bash

```bash
python --version
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

PowerShell activation equivalent: `\.venv\Scripts\Activate.ps1`.

## 2. Static and automated checks

```bash
python -m compileall -q app tests scripts
python -m pytest -q
python -m pytest --cov=app --cov-report=term-missing
```

A failed dependency import is an environment/install issue to resolve before release; do not label the suite passed until the command exits with code 0. Review coverage gaps rather than treating a coverage percentage as proof of detection correctness.

## 3. Run locally

```bash
python -m app.main --host 127.0.0.1 --port 8001
```

Verify in a browser:

- `/` dashboard loads and has styling
- `/docs` Swagger UI loads
- `/health` returns status `ok`
- `/status`, `/events`, `/alerts`, `/incidents`, `/processes` return JSON

Stop with Ctrl+C. Do not run a second server against the same database unless intended.

## 4. Safe end-to-end simulation

1. Back up any wanted files inside `data/sandbox`; the simulator deletes top-level `.txt` and `.locked` files there before writing its disposable sample.
2. Start the server in terminal A.
3. In terminal B, activate `.venv` and run `python scripts/simulate_attack.py` from repository root.
4. Check `/events`, `/status`, `/alerts`, `/incidents` and dashboard. Event capture alone is not proof of a detection; verify score, level, signals, alert, incident, and evidence-copy output.
5. Confirm any quarantined evidence is copied under the configured quarantine directory and originals remain intact.
6. Generate each report format using an actual incident ID from `/incidents`:

```bash
curl -OJ http://127.0.0.1:8001/reports/INCIDENT_ID/json
curl -OJ http://127.0.0.1:8001/reports/INCIDENT_ID/csv
curl -OJ http://127.0.0.1:8001/reports/INCIDENT_ID/html
curl -OJ http://127.0.0.1:8001/reports/INCIDENT_ID/pdf
```

Replace `INCIDENT_ID` with the numeric ID. On Windows PowerShell, use `curl.exe` if `curl` resolves to a PowerShell alias.

## 5. Docker build and smoke test

Dockerfile listens on container port 8000; Compose publishes host port 8001 to container port 8000. From repository root with Docker Desktop running:

```bash
docker --version
docker compose version
docker compose config
docker compose build --no-cache
docker compose up -d
docker compose ps
docker compose logs --tail=200 rdrs
```

Open `http://127.0.0.1:8001/`, `/docs`, and `/health`. Then stop with `docker compose down`. Do not use `docker compose down -v` if you need to preserve data. Inspect logs and fix any startup errors before release.

## 6. GitHub release hygiene

```bash
git status --short
git check-ignore .env .venv data/rdrs.db logs/example.log
git diff --check
```

If new repo only:

```bash
git init
git add .
git status --short
git diff --cached --stat
git commit -m "Prepare RDRS defensive monitor release"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

If repo already exists, use `git remote -v` and do not reinitialize or add a duplicate remote. Check staged files carefully; never commit `.env`, virtualenv, local database, logs, sandbox content, quarantine evidence, or generated reports. If a secret was ever committed, removing it from the latest tree is not enough—rotate it and clean Git history as appropriate.

## 7. Deployment boundary

Current project has no API authentication. Treat Docker as a local/isolated demo only. Before public or production deployment, implement and test authentication/authorization, TLS/reverse proxy, restrictive CORS, rate limiting, secret management, access/audit logging, backups/retention, alert delivery, least-privilege filesystem permissions, health checks, and recovery procedures. Do not mount host-wide directories or change the watched path to personal/system folders.

## 8. PRD acceptance evidence

Keep a table for every PRD requirement with: requirement ID/text, implementation file/endpoint, test command or test name, expected result, actual result, evidence/screenshot, and pass/fail. The ZIP supplied for this audit did not contain a standalone PRD/FSD, so complete traceability cannot be certified from the code archive alone.
