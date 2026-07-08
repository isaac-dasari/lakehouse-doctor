"""File size diagnostics."""

from __future__ import annotations

from pathlib import Path

from lakehouse_doctor.models import Finding, ScanConfig


def check_file_sizes(root: Path, files: list[Path], config: ScanConfig) -> list[Finding]:
    flagged = [path for path in files if path.stat().st_size < config.small_file_threshold_bytes]
    if len(flagged) < config.small_file_min_count:
        return []

    return [
        Finding(
            code="SMALL_FILES",
            severity="warn",
            path=str(root),
            message=f"{len(flagged)} files are below the configured size threshold",
            metadata={
                "file_count": len(flagged),
                "threshold_bytes": config.small_file_threshold_bytes,
            },
        )
    ]
