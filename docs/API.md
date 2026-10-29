# RDRS API reference

## GET /health
Returns service health.

## GET /status
Returns current detector state.

## GET /events?limit=100
Returns recent file events.

## GET /alerts?limit=50
Returns recent alerts.

## GET /incidents?limit=50
Returns recent incidents.

## GET /processes?limit=20
Returns recent process snapshots.

## POST /scan
Re-evaluates/returns current detector status. It does not perform a destructive scan.

## POST /settings
Returns effective runtime settings relevant to the dashboard.

## GET /reports
Lists recent incident data and the report directory.

## GET /reports/{incident_id}/{format}
Formats: `json`, `csv`, `html`, `pdf`.
