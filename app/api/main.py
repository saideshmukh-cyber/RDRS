from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from app.api.auth import (
    ADMIN_USERNAME,
    SESSION_SECRET,
    check_login_rate_limit,
    new_csrf_token,
    require_auth,
    require_csrf,
    verify_password,
)
from app.runtime import get_runtime

app = FastAPI(
    title="RDRS API",
    version="1.0.0",
    description="Defensive ransomware-like behavior detector",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

rt = get_runtime()

production = rt.settings.env.lower() == "production"

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="rdrs_session",
    max_age=60 * 60 * 8,
    same_site="lax",
    https_only=production,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=rt.settings.allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)

STATIC_DIR = Path(__file__).parents[1] / "dashboard" / "static"


class LoginPayload(BaseModel):
    username: str
    password: str


class SettingsUpdate(BaseModel):
    simulation_mode: bool | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/login", include_in_schema=False)
def login_page():
    return FileResponse(STATIC_DIR / "login.html", media_type="text/html")


@app.get("/auth/csrf")
def csrf_token(request: Request):
    token = request.session.get("csrf_token")
    if not token:
        token = new_csrf_token()
        request.session["csrf_token"] = token
    return {"csrf_token": token}


@app.post("/auth/login")
def login(payload: LoginPayload, request: Request):
    require_csrf(request)
    client_ip = request.client.host if request.client else "unknown"
    check_login_rate_limit(client_ip)

    username_ok = hmac_compare(payload.username, ADMIN_USERNAME)
    password_ok = verify_password(payload.password)

    if not username_ok or not password_ok:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    # Replace any pre-login session contents after successful authentication.
    request.session.clear()
    request.session["authenticated"] = True
    request.session["username"] = ADMIN_USERNAME
    request.session["csrf_token"] = new_csrf_token()

    return {"authenticated": True, "username": ADMIN_USERNAME}


@app.post("/auth/logout", dependencies=[Depends(require_auth), Depends(require_csrf)])
def logout(request: Request):
    request.session.clear()
    return {"authenticated": False}


def hmac_compare(left: str, right: str) -> bool:
    import hmac
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


@app.get("/", include_in_schema=False)
def dashboard(request: Request):
    if not request.session.get("authenticated"):
        return RedirectResponse("/login", status_code=303)
    return FileResponse(STATIC_DIR / "index.html", media_type="text/html")


@app.get("/dashboard.css", include_in_schema=False)
def dashboard_css():
    return FileResponse(STATIC_DIR / "dashboard.css", media_type="text/css")


@app.get("/dashboard.js", include_in_schema=False)
def dashboard_js():
    return FileResponse(STATIC_DIR / "dashboard.js", media_type="application/javascript")


@app.get("/status", dependencies=[Depends(require_auth)])
def status():
    return rt.detector.status()


@app.get("/events", dependencies=[Depends(require_auth)])
def events(limit: int = 100):
    return [event_json(x) for x in rt.repo.recent_events(min(max(limit, 1), 500))]


@app.get("/alerts", dependencies=[Depends(require_auth)])
def alerts(limit: int = 50):
    return [alert_json(x) for x in rt.repo.recent_alerts(min(max(limit, 1), 200))]


@app.get("/incidents", dependencies=[Depends(require_auth)])
def incidents(limit: int = 50):
    return [incident_json(x) for x in rt.repo.recent_incidents(min(max(limit, 1), 200))]


@app.get("/processes", dependencies=[Depends(require_auth)])
def processes(limit: int = 20):
    return [
        {
            "pid": x.pid,
            "name": x.name,
            "cpu_percent": x.cpu_percent,
            "memory_percent": x.memory_percent,
            "write_bytes": x.write_bytes,
            "executable": x.executable,
            "parent_pid": x.parent_pid,
            "timestamp": x.timestamp.isoformat(),
        }
        for x in rt.repo.latest_processes(min(max(limit, 1), 100))
    ]


@app.post(
    "/scan",
    dependencies=[Depends(require_auth), Depends(require_csrf)],
)
def scan():
    # Re-evaluate the current in-memory window; no destructive action is performed.
    return rt.detector.status()


@app.get("/reports", dependencies=[Depends(require_auth)])
def reports():
    return {
        "directory": str(rt.settings.reports_dir),
        "incidents": [incident_json(x) for x in rt.repo.recent_incidents(50)],
    }


@app.get("/reports/{incident_id}/{fmt}", dependencies=[Depends(require_auth)])
def report(incident_id: int, fmt: str):
    if fmt not in {"json", "csv", "html", "pdf"}:
        raise HTTPException(400, "Unsupported report format")
    path = getattr(rt.reports, f"{fmt}_report")(incident_id)
    if not path:
        raise HTTPException(404, "Incident not found")
    return FileResponse(path, filename=path.name)


@app.get("/settings", dependencies=[Depends(require_auth)])
def get_settings():
    return {
        "simulation_mode": rt.settings.simulation_mode,
        "watch_paths": [str(p) for p in rt.settings.watch_paths],
        "event_window_seconds": rt.settings.event_window_seconds,
        "quarantine_enabled": rt.settings.quarantine_enabled,
    }


@app.post(
    "/settings",
    dependencies=[Depends(require_auth), Depends(require_csrf)],
)
def update_settings(payload: SettingsUpdate):
    if payload.simulation_mode is not None:
        rt.settings.simulation_mode = payload.simulation_mode
        rt.settings.raw.setdefault("app", {})["simulation_mode"] = payload.simulation_mode
    return get_settings()


def event_json(x):
    return {
        "id": x.id,
        "event_type": x.event_type,
        "path": x.path,
        "old_path": x.old_path,
        "extension": x.extension,
        "timestamp": x.timestamp.isoformat(),
        "entropy": x.entropy,
        "size_bytes": x.size_bytes,
        "extension_changed": x.extension_changed,
    }


def alert_json(x):
    return {
        "id": x.id,
        "timestamp": x.timestamp.isoformat(),
        "level": x.level,
        "score": x.score,
        "message": x.message,
        "signals": json.loads(x.signals_json),
    }


def incident_json(x):
    return {
        "id": x.id,
        "created_at": x.created_at.isoformat(),
        "level": x.level,
        "score": x.score,
        "summary": x.summary,
        "affected_files": json.loads(x.affected_files_json),
        "signals": json.loads(x.signals_json),
        "suspect_process": json.loads(x.suspect_process_json),
        "quarantine_dir": x.quarantine_dir,
    }