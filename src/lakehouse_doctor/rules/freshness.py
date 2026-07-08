"""Freshness diagnostics."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from lakehouse_doctor.models import Finding, ScanConfig


def check_freshness(root: Path, files: list[Path], config: ScanConfig) -> list[Finding]:
    if not files:
        return []

    newest_mtime = max(path.stat().st_mtime for path in files)
    newest = datetime.fromtimestamp(newest_mtime, tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    age_days = (now - newest).days

    if age_days <= config.freshness_days:
        return []

    return [
        Finding(
            code="STALE_TABLE",
            severity="warn",
            path=str(root),
            message=f"Newest file is {age_days} days old",
            metadata={"age_days": age_days, "freshness_days": config.freshness_days},
        )
    ]
