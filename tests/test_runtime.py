from app.runtime import Runtime


class FakeMonitor:
    def __init__(self):
        self.start_calls = 0
        self.stop_calls = 0

    def start(self):
        self.start_calls += 1

    def stop(self):
        self.stop_calls += 1


def make_runtime_for_test():
    """Create a Runtime without opening a database or starting real monitors."""
    runtime = Runtime.__new__(Runtime)
    runtime.file_monitor = FakeMonitor()
    runtime.process_monitor = FakeMonitor()
    runtime.started = False
    return runtime


def test_start_starts_both_monitors():
    runtime = make_runtime_for_test()

    runtime.start()

    assert runtime.file_monitor.start_calls == 1
    assert runtime.process_monitor.start_calls == 1
    assert runtime.started is True


def test_start_twice_does_not_start_monitors_twice():
    runtime = make_runtime_for_test()

    runtime.start()
    runtime.start()

    assert runtime.file_monitor.start_calls == 1
    assert runtime.process_monitor.start_calls == 1
    assert runtime.started is True


def test_stop_stops_both_monitors():
    runtime = make_runtime_for_test()

    runtime.start()
    runtime.stop()

    assert runtime.file_monitor.stop_calls == 1
    assert runtime.process_monitor.stop_calls == 1
    assert runtime.started is False


def test_stop_twice_does_not_stop_monitors_twice():
    runtime = make_runtime_for_test()

    runtime.start()
    runtime.stop()
    runtime.stop()

    assert runtime.file_monitor.stop_calls == 1
    assert runtime.process_monitor.stop_calls == 1
    assert runtime.started is False


def test_stop_before_start_does_nothing():
    runtime = make_runtime_for_test()

    runtime.stop()

    assert runtime.file_monitor.stop_calls == 0
    assert runtime.process_monitor.stop_calls == 0
    assert runtime.started is False
