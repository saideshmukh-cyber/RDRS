from __future__ import annotations
from dataclasses import dataclass


@dataclass(slots=True)
class ScoreResult:
    score: int
    level: str
    signals: list[str]


class ScoringEngine:
    def __init__(self, scoring: dict, thresholds: dict):
        self.scoring = scoring
        self.thresholds = thresholds

    def calculate(self, *, modified_count: int, rename_count: int, extension_change_count: int,
                  avg_entropy: float, cpu_spike: bool = False, unknown_program: bool = False) -> ScoreResult:
        signals=[]; score=0
        if modified_count >= self.thresholds["modified_files_per_window"]:
            score += self.scoring["rapid_encryption"]; signals.append("rapid_encryption")
        if rename_count >= self.thresholds["rename_count_per_window"]:
            score += self.scoring["mass_rename"]; signals.append("mass_rename")
        if extension_change_count >= self.thresholds["extension_change_count_per_window"]:
            # Extension changes strengthen the mass-rename signal but do not add
            # a second copy of the same configured weight.
            if "mass_rename" not in signals:
                score += self.scoring["mass_rename"]
                signals.append("mass_rename")
        if avg_entropy >= self.thresholds["high_entropy"]:
            score += self.scoring["high_entropy"]; signals.append("high_entropy")
        if cpu_spike:
            score += self.scoring["cpu_spike"]; signals.append("cpu_spike")
        if unknown_program:
            score += self.scoring["unknown_program"]; signals.append("unknown_program")
        score=min(100, int(score))
        if score >= self.scoring["warning_max_exclusive"]:
            level="Critical"
        elif score >= self.scoring["normal_max_exclusive"]:
            level="Warning"
        else:
            level="Normal"
        return ScoreResult(score, level, signals)
