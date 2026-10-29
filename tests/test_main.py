import sys
from types import SimpleNamespace
from unittest.mock import Mock

import app.main as main_module


def make_runtime():
    runtime = Mock()
    runtime.settings = SimpleNamespace(host="127.0.0.1", port=8001)
    return runtime


def test_main_starts_runtime_and_runs_api_with_default_settings(monkeypatch):
    runtime = make_runtime()
    monkeypatch.setattr(main_module, "get_runtime", lambda: runtime)
    uvicorn_run = Mock()
    monkeypatch.setattr(main_module.uvicorn, "run", uvicorn_run)
    monkeypatch.setattr(sys, "argv", ["rdrs"])

    main_module.main()

    runtime.start.assert_called_once_with()
    uvicorn_run.assert_called_once_with(
        "app.api.main:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
    )


def test_main_uses_custom_host_and_port(monkeypatch):
    runtime = make_runtime()
    monkeypatch.setattr(main_module, "get_runtime", lambda: runtime)
    uvicorn_run = Mock()
    monkeypatch.setattr(main_module.uvicorn, "run", uvicorn_run)
    monkeypatch.setattr(
        sys, "argv", ["rdrs", "--host", "0.0.0.0", "--port", "9000"]
    )

    main_module.main()

    uvicorn_run.assert_called_once_with(
        "app.api.main:app",
        host="0.0.0.0",
        port=9000,
        reload=False,
    )


def test_main_no_api_stops_runtime_after_keyboard_interrupt(monkeypatch):
    runtime = make_runtime()
    monkeypatch.setattr(main_module, "get_runtime", lambda: runtime)
    monkeypatch.setattr(sys, "argv", ["rdrs", "--no-api"])

    def interrupt_sleep(_seconds):
        raise KeyboardInterrupt

    monkeypatch.setattr("time.sleep", interrupt_sleep)
    uvicorn_run = Mock()
    monkeypatch.setattr(main_module.uvicorn, "run", uvicorn_run)

    result = main_module.main()

    runtime.start.assert_called_once_with()
    runtime.stop.assert_called_once_with()
    uvicorn_run.assert_not_called()
    assert result is None
