
import threading
import pytest
from codomyrmex.telemetry.dashboard.slo import SLOTracker, SLIType

def test_slo_tracker_recoding_concurrency():
    """Verify thread safety of SLOTracker.record_event."""
    tracker = SLOTracker()
    tracker.create_slo("concurrent_slo", "Concurrent SLO", SLIType.AVAILABILITY, 99.0)
    
    def worker():
        for _ in range(100):
            tracker.record_event("concurrent_slo", is_good=True)
            tracker.record_event("concurrent_slo", is_good=False)

    threads = []
    for _ in range(10):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    status = tracker.get_status("concurrent_slo")
    assert status["total_events"] == 2000  # 10 threads * 100 iterations * 2 events
    assert status["good_events"] == 1000   # 10 threads * 100 iterations * 1 good event

def test_slo_creation_concurrency():
    """Verify thread safety of SLOTracker.create_slo."""
    tracker = SLOTracker()
    
    def worker(i):
        tracker.create_slo(f"slo_{i}", f"SLO {i}", SLIType.LATENCY, 95.0)

    threads = []
    for i in range(100):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Verify all SLOs were created
    assert len(tracker._slos) == 100
