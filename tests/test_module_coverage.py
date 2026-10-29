
from types import SimpleNamespace

import pytest

from app.core.entropy import file_entropy, shannon_entropy
from app.core.models import FileEventData
from app.database.repository import Repository
from app.detectors.file_monitor import RDRSEventHandler
from app.detectors.process_monitor import ProcessMonitor
from app.reports.service import ReportService


# ---------- Entropy edge cases ----------

def test_entropy_single_byte_and_binary_data():
    assert shannon_entropy(b"\x00" * 100) == 0.0
    assert 0.0 <= shannon_entropy(b"\x00\x01\x02\x03") <= 8.0


def test_file_entropy_missing_file_returns_none(tmp_path):
    missing = tmp_path / "does-not-exist.bin"
    assert file_entropy(missing) is None


def test_file_entropy_reads_file_prefix(tmp_path):
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"A" * 100)

    assert file_entropy(sample, sample_bytes=10) == 0.0


# ---------- Repository reads and writes ----------

def test_repository_adds_and_reads_file_event(test_runtime, tmp_path):
    _, repo, _ = test_runtime
    event = FileEventData(
        event_type="created",
        path=str(tmp_path / "sample.txt"),
        extension=".txt",
        entropy=1.0,
        size_bytes=12,
    )

    saved = repo.add_event(event)
    assert saved.id is not None

    events = repo.recent_events()
    assert any(item.path == event.path for item in events)



from datetime import datetime, timezone

def test_repository_process_snapshot_and_latest_processes(test_runtime):
    _, repo, _ = test_runtime

    repo.add_process_snapshot({
        "pid": 12345,
        "name": "rdrs-test-process",
        "cpu_percent": 1.5,
        "memory_percent": 2.0,
        "write_bytes": 100,
        "executable": "test-process.exe",
        "parent_pid": 1,
        "timestamp": datetime.now(timezone.utc),
    })

    processes = repo.latest_processes()
    assert any(item.pid == 12345 for item in processes)


def test_repository_alert_and_incident_round_trip(test_runtime):
    _, repo, _ = test_runtime

    alert = repo.add_alert(
        level="Warning",
        score=50,
        message="Test alert",
        signals=["high_entropy"],
    )
    assert alert.id is not None
    assert any(item.id == alert.id for item in repo.recent_alerts())

    incident = repo.add_incident(
        score=80,
        level="Critical",
        summary="Test incident",
        affected_files=["sample.locked"],
        signals=["high_entropy", "mass_rename"],
        process={"name": "rdrs-test-process"},
        quarantine_dir=None,
    )
    assert incident.id is not None

    fetched = repo.get_incident(incident.id)
    assert fetched is not None
    assert fetched.level == "Critical"
    assert any(item.id == incident.id for item in repo.recent_incidents())


# ---------- Filesystem event handling ----------

def test_file_handler_emits_created_file_event(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("hello", encoding="utf-8")
    received = []

    handler = RDRSEventHandler(received.append, sample_bytes=1024)
    handler.on_created(SimpleNamespace(src_path=str(sample), is_directory=False))

    assert len(received) == 1
    assert received[0].event_type == "created"
    assert received[0].path == str(sample)
    assert received[0].extension == ".txt"


def test_file_handler_ignores_directory(tmp_path):
    directory = tmp_path / "folder"
    directory.mkdir()
    received = []

    handler = RDRSEventHandler(received.append, sample_bytes=1024)
    handler.on_created(SimpleNamespace(src_path=str(directory), is_directory=True))

    assert received == []


def test_file_handler_emits_deleted_event(tmp_path):
    sample = tmp_path / "removed.txt"
    received = []
    handler = RDRSEventHandler(received.append, sample_bytes=1024)

    handler.on_deleted(SimpleNamespace(src_path=str(sample), is_directory=False))

    assert len(received) == 1
    assert received[0].event_type == "deleted"


# ---------- Process snapshot handling ----------

def test_process_monitor_snapshot_records_process(test_runtime, monkeypatch):
    _, repo, _ = test_runtime

    class FakeProcess:
        info = {
            "pid": 2468,
            "name": "fake-process",
            "cpu_percent": 3.5,
            "memory_percent": 1.2,
            "exe": "fake.exe",
            "ppid": 1,
        }

        def is_running(self):
            return True

        def io_counters(self):
            return SimpleNamespace(write_bytes=512)

    monkeypatch.setattr(
        "app.detectors.process_monitor.psutil.process_iter",
        lambda fields: [FakeProcess()],
    )

    monitor = ProcessMonitor(repo)
    monitor._snapshot()

    processes = repo.latest_processes()
    saved = next(item for item in processes if item.pid == 2468)

    assert saved.name == "fake-process"
    assert saved.write_bytes == 512


def test_process_monitor_skips_access_denied_process(test_runtime, monkeypatch):
    import psutil

    _, repo, _ = test_runtime

    class DeniedProcess:
        info = {
            "pid": 9999,
            "name": "inaccessible",
            "cpu_percent": 0,
            "memory_percent": 0,
            "exe": "",
            "ppid": 1,
        }

        def is_running(self):
            raise psutil.AccessDenied(pid=9999)

    monkeypatch.setattr(
        "app.detectors.process_monitor.psutil.process_iter",
        lambda fields: [DeniedProcess()],
    )

    monitor = ProcessMonitor(repo)
    monitor._snapshot()

    assert not any(item.pid == 9999 for item in repo.latest_processes())


# ---------- Report generation ----------

def test_report_service_generates_all_formats(test_runtime):
    settings, repo, _ = test_runtime

    incident = repo.add_incident(
        score=85,
        level="Critical",
        summary="Test report incident",
        affected_files=["example.locked"],
        signals=["high_entropy"],
        process={"name": "test-process"},
        quarantine_dir=None,
    )

    reports = ReportService(settings, repo)

    json_path = reports.json_report(incident.id)
    csv_path = reports.csv_report(incident.id)
    html_path = reports.html_report(incident.id)
    pdf_path = reports.pdf_report(incident.id)

    for path in (json_path, csv_path, html_path, pdf_path):
        assert path is not None
        assert path.exists()
        assert path.stat().st_size > 0

    assert "Critical" in json_path.read_text(encoding="utf-8")
    assert "incident_id" in csv_path.read_text(encoding="utf-8")
    assert "Test report incident" in html_path.read_text(encoding="utf-8")
    assert pdf_path.read_bytes().startswith(b"%PDF")


def test_report_service_returns_none_for_unknown_incident(test_runtime):
    settings, repo, _ = test_runtime
    reports = ReportService(settings, repo)

    assert reports.data(999999) is None
    assert reports.json_report(999999) is None
    assert reports.csv_report(999999) is None
    assert reports.html_report(999999) is None
    assert reports.pdf_report(999999) is None


# Additional filesystem event tests

def test_file_handler_emits_modified_event(tmp_path):
    sample = tmp_path / "modified.txt"
    sample.write_text("updated content", encoding="utf-8")
    received = []

    handler = RDRSEventHandler(received.append, sample_bytes=1024)
    handler.on_modified(
        SimpleNamespace(src_path=str(sample), is_directory=False)
    )

    assert len(received) == 1
    assert received[0].event_type == "modified"
    assert received[0].path == str(sample)


def test_file_handler_emits_renamed_event(tmp_path):
    old_path = tmp_path / "old.txt"
    new_path = tmp_path / "new.txt"
    new_path.write_text("renamed content", encoding="utf-8")
    received = []

    handler = RDRSEventHandler(received.append, sample_bytes=1024)
    handler.on_moved(
        SimpleNamespace(
            src_path=str(old_path),
            dest_path=str(new_path),
            is_directory=False,
        )
    )

    assert len(received) == 1
    assert received[0].event_type == "renamed"
    assert received[0].path == str(new_path)
    assert received[0].old_path == str(old_path)


def test_file_handler_ignores_moved_directory(tmp_path):
    old_dir = tmp_path / "old_folder"
    new_dir = tmp_path / "new_folder"
    new_dir.mkdir()
    received = []

    handler = RDRSEventHandler(received.append, sample_bytes=1024)
    handler.on_moved(
        SimpleNamespace(
            src_path=str(old_dir),
            dest_path=str(new_dir),
            is_directory=True,
        )
    )

    assert received == []


def test_file_monitor_start_and_stop(tmp_path, monkeypatch):
    import app.detectors.file_monitor as monitor_module

    class FakeObserver:
        def __init__(self):
            self.scheduled = []
            self.started = False
            self.stopped = False
            self.joined = False

        def schedule(self, handler, path, recursive):
            self.scheduled.append((handler, path, recursive))

        def start(self):
            self.started = True

        def stop(self):
            self.stopped = True

        def join(self, timeout=None):
            self.joined = True

    fake_observer = FakeObserver()
    monkeypatch.setattr(
        monitor_module, "Observer", lambda: fake_observer
    )

    watch_path = tmp_path / "watch"
    monitor = monitor_module.FileMonitor(
        [watch_path], lambda event: None, sample_bytes=1024
    )

    monitor.start()

    assert watch_path.is_dir()
    assert fake_observer.started
    assert len(fake_observer.scheduled) == 1
    assert fake_observer.scheduled[0][2] is True

    monitor.stop()

    assert fake_observer.stopped
    assert fake_observer.joined
    assert monitor._started is False


def test_file_monitor_stop_before_start(tmp_path, monkeypatch):
    import app.detectors.file_monitor as monitor_module

    class FakeObserver:
        def stop(self):
            raise AssertionError("stop should not be called")

        def join(self, timeout=None):
            raise AssertionError("join should not be called")

    monkeypatch.setattr(
        monitor_module, "Observer", FakeObserver
    )

    monitor = monitor_module.FileMonitor(
        [tmp_path / "watch"], lambda event: None, sample_bytes=1024
    )

    monitor.stop()
    assert monitor._started is False


def test_file_handler_ignores_empty_path(tmp_path):
    handler = RDRSEventHandler(
        lambda event: None, sample_bytes=1024
    )

    handler._emit("created", None)
    handler._emit("created", None, old_path=None)


def test_file_handler_ignores_directory(tmp_path):
    directory = tmp_path / "folder"
    directory.mkdir()
    emitted = []

    handler = RDRSEventHandler(
        emitted.append, sample_bytes=1024
    )

    handler._emit("created", str(directory))

    assert emitted == []


def test_process_monitor_snapshot_skips_inaccessible_process(monkeypatch):
    import psutil
    import app.detectors.process_monitor as process_module

    class FakeProcess:
        info = {
            "pid": 123,
            "name": "inaccessible-process",
            "cpu_percent": 0,
            "memory_percent": 0,
            "exe": "",
            "ppid": 1,
        }

        def is_running(self):
            return True

        def io_counters(self):
            raise psutil.AccessDenied(pid=123)

    class FakeRepository:
        def __init__(self):
            self.snapshots = []

        def add_process_snapshot(self, snapshot):
            self.snapshots.append(snapshot)

    repository = FakeRepository()
    monkeypatch.setattr(
        process_module.psutil,
        "process_iter",
        lambda fields: [FakeProcess()],
    )

    monitor = process_module.ProcessMonitor(repository)
    monitor._snapshot()

    assert repository.snapshots == []


def test_process_monitor_run_handles_snapshot_error(monkeypatch):
    import app.detectors.process_monitor as process_module

    class FakeStopEvent:
        def __init__(self):
            self.calls = 0

        def is_set(self):
            self.calls += 1
            return self.calls > 1

        def wait(self, interval):
            return False

    monitor = process_module.ProcessMonitor(
        repository=None, interval=0
    )
    monitor._stop = FakeStopEvent()

    def fail_snapshot():
        raise RuntimeError("simulated snapshot failure")

    monkeypatch.setattr(monitor, "_snapshot", fail_snapshot)

    # The loop should log the exception and exit cleanly.
    monitor._run()

    assert monitor._stop.calls >= 2


def test_process_monitor_stop_without_thread():
    import app.detectors.process_monitor as process_module

    monitor = process_module.ProcessMonitor(repository=None)
    monitor.stop()

    assert monitor._stop.is_set()


from types import SimpleNamespace
from pathlib import Path

from app.detectors.responder import IncidentResponder


def test_responder_log_only_mode(test_runtime, tmp_path):
    settings, repo, _ = test_runtime
    settings.raw["response"]["quarantine_enabled"] = False
    responder = IncidentResponder(settings, repo)
    score_result = SimpleNamespace(
        score=90,
        level="critical",
        signals=["high_entropy"],
    )

    incident = responder.respond(score_result, [], {})

    assert incident.id is not None
    assert incident.quarantine_dir is None


def test_responder_skips_missing_files(test_runtime, tmp_path):
    settings, repo, _ = test_runtime
    settings.raw["response"]["quarantine_enabled"] = True
    settings.raw["response"]["quarantine_dir"] = str(tmp_path / "quarantine")
    responder = IncidentResponder(settings, repo)
    score_result = SimpleNamespace(
        score=90,
        level="critical",
        signals=["rapid_changes"],
    )

    missing_file = tmp_path / "does_not_exist.txt"
    incident = responder.respond(score_result, [str(missing_file)], {})

    assert incident.id is not None
    assert incident.quarantine_dir is not None
    assert list(Path(incident.quarantine_dir).iterdir()) == []


def test_responder_preserves_duplicate_filenames(test_runtime, tmp_path):
    settings, repo, _ = test_runtime
    settings.raw["response"]["quarantine_enabled"] = True
    settings.raw["response"]["quarantine_dir"] = str(tmp_path / "quarantine")
    responder = IncidentResponder(settings, repo)
    score_result = SimpleNamespace(
        score=95,
        level="critical",
        signals=["mass_file_changes"],
    )

    first_dir = tmp_path / "source_a"
    second_dir = tmp_path / "source_b"
    first_dir.mkdir()
    second_dir.mkdir()

    first_file = first_dir / "evidence.txt"
    second_file = second_dir / "evidence.txt"
    first_file.write_text("first evidence")
    second_file.write_text("second evidence")

    incident = responder.respond(
        score_result,
        [str(first_file), str(second_file)],
        {},
    )

    saved_files = sorted(Path(incident.quarantine_dir).glob("*.txt"))
    assert len(saved_files) == 2
    assert {file.read_text() for file in saved_files} == {
        "first evidence",
        "second evidence",
    }


def test_responder_handles_copy_oserror(test_runtime, tmp_path, monkeypatch):
    import app.detectors.responder as responder_module

    settings, repo, _ = test_runtime
    settings.raw["response"]["quarantine_enabled"] = True
    settings.raw["response"]["quarantine_dir"] = str(tmp_path / "quarantine")
    responder = IncidentResponder(settings, repo)
    score_result = SimpleNamespace(
        score=95,
        level="critical",
        signals=["suspicious_writes"],
    )

    evidence = tmp_path / "evidence.txt"
    evidence.write_text("test evidence")

    def fail_copy(*args, **kwargs):
        raise OSError("simulated copy failure")

    monkeypatch.setattr(responder_module.shutil, "copy2", fail_copy)

    incident = responder.respond(score_result, [str(evidence)], {})

    assert incident.id is not None
    assert incident.quarantine_dir is not None
    assert list(Path(incident.quarantine_dir).iterdir()) == []