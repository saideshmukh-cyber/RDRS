from __future__ import annotations

from dataclasses import asdict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from app.runtime import get_runtime

app=FastAPI(title="RDRS API", version="1.0.0", description="Defensive ransomware-like behavior detector")
rt=get_runtime()
app.add_middleware(CORSMiddleware, allow_origins=rt.settings.allow_origins, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])


def event_json(x):
    return {"id":x.id,"event_type":x.event_type,"path":x.path,"old_path":x.old_path,"extension":x.extension,
            "timestamp":x.timestamp.isoformat(),"entropy":x.entropy,"size_bytes":x.size_bytes,"extension_changed":x.extension_changed}

def alert_json(x):
    import json
    return {"id":x.id,"timestamp":x.timestamp.isoformat(),"level":x.level,"score":x.score,"message":x.message,"signals":json.loads(x.signals_json)}

def incident_json(x):
    import json
    return {"id":x.id,"created_at":x.created_at.isoformat(),"level":x.level,"score":x.score,"summary":x.summary,
            "affected_files":json.loads(x.affected_files_json),"signals":json.loads(x.signals_json),"suspect_process":json.loads(x.suspect_process_json),"quarantine_dir":x.quarantine_dir}

STATIC_DIR = Path(__file__).parents[1] / "dashboard" / "static"

@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "index.html", media_type="text/html; charset=utf-8")

@app.get("/dashboard.css", include_in_schema=False)
def dashboard_css():
    return FileResponse(STATIC_DIR / "dashboard.css", media_type="text/css; charset=utf-8")

@app.get("/dashboard.js", include_in_schema=False)
def dashboard_js():
    return FileResponse(STATIC_DIR / "dashboard.js", media_type="application/javascript; charset=utf-8")

@app.get("/health")
def health(): return {"status":"ok","service":"rdrs"}

@app.get("/status")
def status(): return rt.detector.status()

@app.get("/events")
def events(limit:int=100): return [event_json(x) for x in rt.repo.recent_events(min(limit,500))]

@app.get("/alerts")
def alerts(limit:int=50): return [alert_json(x) for x in rt.repo.recent_alerts(min(limit,200))]

@app.get("/incidents")
def incidents(limit:int=50): return [incident_json(x) for x in rt.repo.recent_incidents(min(limit,200))]

@app.get("/processes")
def processes(limit:int=20):
    return [{"pid":x.pid,"name":x.name,"cpu_percent":x.cpu_percent,"memory_percent":x.memory_percent,"write_bytes":x.write_bytes,"executable":x.executable,"parent_pid":x.parent_pid,"timestamp":x.timestamp.isoformat()} for x in rt.repo.latest_processes(min(limit,100))]

@app.post("/scan")
def scan():
    # Re-evaluate the current in-memory window; no destructive action is performed.
    return rt.detector.status()

@app.get("/reports")
def reports():
    return {"directory":str(rt.settings.reports_dir),"incidents":[incident_json(x) for x in rt.repo.recent_incidents(50)]}

@app.get("/reports/{incident_id}/{fmt}")
def report(incident_id:int, fmt:str):
    if fmt not in {"json","csv","html","pdf"}: raise HTTPException(400,"Unsupported report format")
    path=getattr(rt.reports, f"{fmt}_report")(incident_id)
    if not path: raise HTTPException(404,"Incident not found")
    return FileResponse(path, filename=path.name)

class SettingsUpdate(BaseModel):
    # Only allow the safe simulation flag to be changed at runtime.
    # Monitoring paths and thresholds remain controlled by config.yaml.
    simulation_mode: bool | None = None


@app.get("/settings")
def get_settings():
    return {"simulation_mode": rt.settings.simulation_mode,
            "watch_paths": [str(p) for p in rt.settings.watch_paths],
            "event_window_seconds": rt.settings.event_window_seconds,
            "quarantine_enabled": rt.settings.quarantine_enabled}


@app.post("/settings")
def update_settings(payload: SettingsUpdate):
    if payload.simulation_mode is not None:
        rt.settings.simulation_mode = payload.simulation_mode
        rt.settings.raw.setdefault("app", {})["simulation_mode"] = payload.simulation_mode
    return get_settings()
