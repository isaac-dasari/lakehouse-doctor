"""Shared data models."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    path: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScanConfig:
    root_path: Path
    small_file_threshold_bytes: int = 128 * 1024
    small_file_min_count: int = 5
    freshness_days: int = 30
    partition_skew_ratio: float = 3.0
    primary_key: str | None = None


@dataclass(frozen=True)
class ScanResult:
    root_path: str
    table_count: int
    file_count: int
    total_bytes: int
    findings: list[Finding]
    format_counts: dict[str, int] = field(default_factory=dict)
    table_file_counts: dict[str, int] = field(default_factory=dict)

    def severity_counts(self) -> dict[str, int]:
        counts = Counter(finding.severity for finding in self.findings)
        return {"error": counts.get("error", 0), "warn": counts.get("warn", 0), "info": counts.get("info", 0)}

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_path": self.root_path,
            "table_count": self.table_count,
            "file_count": self.file_count,
            "total_bytes": self.total_bytes,
            "format_counts": self.format_counts,
            "table_file_counts": self.table_file_counts,
            "severity_counts": self.severity_counts(),
            "findings": [finding.to_dict() for finding in self.findings],
        }
