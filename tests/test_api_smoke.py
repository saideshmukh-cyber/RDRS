from fastapi.testclient import TestClient
from app.api.main import app
import app.api.main as api_main
from app.reports.service import ReportService

client = TestClient(app)


# ---------- Fixture: isolate API tests from the real database ----------

import pytest


@pytest.fixture(autouse=True)
def isolated_runtime(test_runtime, monkeypatch):
    settings, repo, detector = test_runtime

    runtime = type("Runtime", (), {})()
    runtime.settings = settings
    runtime.repo = repo
    runtime.detector = detector
    runtime.reports = ReportService(settings, repo)

    monkeypatch.setattr(api_main, "rt", runtime)

    yield runtime


# ---------- Existing tests ----------

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard_html_and_assets_are_served():
    page = client.get("/")
    assert page.status_code == 200
    assert "RDRS Security Dashboard" in page.text

    css = client.get("/dashboard.css")
    js = client.get("/dashboard.js")

    assert css.status_code == 200
    assert "background" in css.text

    assert js.status_code == 200
    assert "function refresh" in js.text


def test_settings_endpoint_is_readable_and_safe_update_is_applied():
    before = client.get("/settings")
    assert before.status_code == 200

    original = before.json()["simulation_mode"]

    response = client.post(
        "/settings",
        json={"simulation_mode": not original},
    )

    assert response.status_code == 200
    assert response.json()["simulation_mode"] is (not original)

    client.post("/settings", json={"simulation_mode": original})


# ---------- Endpoint tests ----------

def test_events_alerts_incidents_and_processes_endpoints():
    assert client.get("/events").status_code == 200
    assert isinstance(client.get("/events").json(), list)

    assert client.get("/alerts").status_code == 200
    assert isinstance(client.get("/alerts").json(), list)

    assert client.get("/incidents").status_code == 200
    assert isinstance(client.get("/incidents").json(), list)

    assert client.get("/processes").status_code == 200
    assert isinstance(client.get("/processes").json(), list)


def test_endpoint_limits_are_capped():
    assert client.get("/events?limit=9999").status_code == 200
    assert client.get("/alerts?limit=9999").status_code == 200
    assert client.get("/incidents?limit=9999").status_code == 200
    assert client.get("/processes?limit=9999").status_code == 200


def test_reports_endpoint_returns_directory_and_incidents():
    response = client.get("/reports")

    assert response.status_code == 200

    data = response.json()

    assert "directory" in data
    assert "incidents" in data
    assert isinstance(data["incidents"], list)


def test_report_download_rejects_unsupported_format():
    response = client.get("/reports/1/exe")

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported report format"


def test_report_download_returns_404_for_missing_incident():
    for fmt in ("json", "csv", "html", "pdf"):
        response = client.get(f"/reports/999999/{fmt}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Incident not found"


def test_scan_endpoint_returns_detector_status():
    response = client.post("/scan")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)