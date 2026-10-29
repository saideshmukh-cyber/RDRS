from datetime import datetime, timezone
from app.core.models import FileEventData

def test_simulated_burst_creates_critical_incident(test_runtime, tmp_path):
    settings, repo, detector=test_runtime
    sandbox=tmp_path/"sandbox"; sandbox.mkdir()
    for i in range(25):
        p=sandbox/f"file_{i}.locked"; p.write_bytes(bytes(range(256))*80)
        e=FileEventData(event_type="modified", path=str(p), extension=".locked", entropy=7.8, size_bytes=p.stat().st_size)
        detector.handle_event(e)
        old=sandbox/f"file_{i}.txt"
        r=FileEventData(event_type="renamed", path=str(p), old_path=str(old), extension=".locked", entropy=7.8, size_bytes=p.stat().st_size)
        detector.handle_event(r)
    incidents=repo.recent_incidents()
    assert incidents
    assert incidents[0].level=="Critical"
    assert incidents[0].score>=70
    quarantine=tmp_path/"quarantine"
    assert quarantine.exists()
    assert any(quarantine.rglob("*.locked"))
