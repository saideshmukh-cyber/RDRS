from app.detectors.scoring import ScoringEngine

def test_normal_score():
    s=ScoringEngine({"rapid_encryption":40,"mass_rename":30,"high_entropy":25,"cpu_spike":15,"unknown_program":10,"normal_max_exclusive":40,"warning_max_exclusive":70},{"modified_files_per_window":20,"rename_count_per_window":10,"extension_change_count_per_window":5,"high_entropy":7.2,"cpu_percent":80})
    r=s.calculate(modified_count=1,rename_count=0,extension_change_count=0,avg_entropy=2)
    assert r.score==0 and r.level=="Normal"

def test_critical_score():
    s=ScoringEngine({"rapid_encryption":40,"mass_rename":30,"high_entropy":25,"cpu_spike":15,"unknown_program":10,"normal_max_exclusive":40,"warning_max_exclusive":70},{"modified_files_per_window":20,"rename_count_per_window":10,"extension_change_count_per_window":5,"high_entropy":7.2,"cpu_percent":80})
    r=s.calculate(modified_count=25,rename_count=12,extension_change_count=8,avg_entropy=7.8)
    assert r.score==95 and r.level=="Critical"
