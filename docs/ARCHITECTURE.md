# Architecture

RDRS is split into configuration/core, monitoring/detection, persistence, API/dashboard, and reporting.

## Data flow

1. `watchdog` detects a filesystem event.
2. `FileMonitor` samples file metadata and entropy.
3. `DetectionEngine` stores the event and places it in a 60-second sliding window.
4. The scoring engine evaluates transparent rules.
5. Warning/Critical results create alerts.
6. Critical results create an incident and copy evidence to quarantine.
7. FastAPI exposes state to humans and the dashboard.
8. `ReportService` renders incident records.

## Important design choice

A filesystem event does not inherently identify the process that caused it on every platform. Therefore the current implementation stores process snapshots independently and uses them as supporting telemetry rather than claiming exact process attribution.

## Safety boundary

The response action is copy-only quarantine. There is no process termination, encryption, propagation, persistence, or destructive remediation.
