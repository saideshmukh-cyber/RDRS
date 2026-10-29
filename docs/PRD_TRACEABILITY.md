# RDRS FSD v1.0 traceability and acceptance plan

This matrix is based on `RDRS_Functional_Specification_Document_FSD.docx` and its companion hands-on build guide supplied by the project owner. “Implemented in source” is not the same as “verified”; run the acceptance tests below on the target machine before sign-off.

| Requirement | Current implementation | Acceptance evidence / gap |
|---|---|---|
| FR-1 Load `config.yaml` | `app/core/config.py` | Change a sandbox-only setting in config and restart; verify `/settings` or `/status`. |
| FR-2 Real-time create/modify/delete/rename | `app/detectors/file_monitor.py` | Create, edit, rename, delete throwaway files under `data/sandbox`; verify all four event types in `/events`. |
| FR-3 Shannon entropy | `app/core/entropy.py` | `tests/test_entropy.py`; also test text and random bytes. |
| FR-4 Process metadata via psutil | `app/detectors/process_monitor.py` | Verify `/processes`; access-denied processes must be skipped without crashing. |
| FR-5 SQLite events/processes/alerts/incidents | `app/database/` | Verify records survive an app restart. Scores are represented in alerts/incidents; there is no separate score-history table in this version. |
| FR-6 Sliding event window | `app/detectors/engine.py` | Generate a burst, verify `/status.window_events` rises and ages out after the configured window. |
| FR-7 Weighted 0–100 score | `app/detectors/scoring.py` | `tests/test_scoring.py`; verify configured weights and caps. |
| FR-8 Alerts and incidents | `app/detectors/engine.py`, `responder.py` | `tests/test_integration.py`; confirm one controlled burst creates a critical incident. |
| FR-9 Quarantine copy in simulation | `app/detectors/responder.py` | Compare hashes of original sandbox files before/after; verify evidence copies. This is evidence preservation, not a secure OS quarantine. |
| FR-10 REST API | `app/api/main.py` | Smoke test `/health`, `/status`, `/events`, `/alerts`, `/incidents`, `/processes`, `/reports`, `/scan`, `/settings`. |
| FR-11 Live dashboard | `app/dashboard/static/` | Browser check; JavaScript refreshes every three seconds. Screenshot the dashboard during a test. |
| FR-12 JSON/CSV reports | `app/reports/service.py` | Download a report for a real incident and validate its contents. HTML/PDF are extra formats. |
| FR-13 Tests and Docker | `tests/`, `Dockerfile`, `docker-compose.yml`, GitHub workflow | Run pytest locally and `docker compose up --build`; check logs and `/health`. |
| NFR: simulation by default | `config.yaml`, `.env.example`, Compose | Confirm `/settings` reports `simulation_mode: true`. Keep it enabled for demo. |
| NFR: comprehensive logging | `app/core/logging.py` | Inspect `logs/` after a simulated run; confirm event, alert, error, audit channels are created. |
| NFR: modular/docs | `app/`, `README.md`, `docs/` | Review architecture and setup docs. |

## Known gaps / do not overclaim

- Unknown-program scoring is not yet based on a configured allowlist/baseline: the detector currently passes `unknown_program=False`. Treat this signal as **not implemented** until a defensible baseline and tests are added.
- There is no separate persisted score-history table; scores are stored with alert and incident records.
- `/scan` currently returns the current detector status rather than scanning an arbitrary path. `/settings` only updates the runtime simulation flag; it does not persist changes back to `config.yaml` or reconfigure running monitors.
- Process CPU readings are snapshots and may be zero on an initial psutil sample. Treat them as supporting evidence, not a standalone reliable signal.
- A copy to a folder named quarantine is not OS-level isolation and does not prevent a process from modifying the original file.
- The current API has no authentication. Do not expose it to the public internet without an authenticated, TLS-protected deployment and a security review.

## Final acceptance checklist

- [ ] `python -m compileall -q app tests scripts`
- [ ] `python -m pytest -q` passes on Python 3.12+
- [ ] `python -m pytest --cov=app --cov-report=term-missing` recorded; target >=90% per guide (do not claim it unless measured)
- [ ] Sandbox-only burst reaches Critical and creates alert + incident
- [ ] Original sandbox file hashes are unchanged by response; evidence copies exist
- [ ] JSON and CSV report files are valid and contain incident timeline/signals/files/process details as available
- [ ] Dashboard status and tables update during the run
- [ ] Docker build starts and `/health` succeeds at `http://127.0.0.1:8001/health`
- [ ] `.env`, `.venv`, database files, logs, quarantine evidence, and generated reports are not committed
- [ ] GitHub Actions workflow passes
