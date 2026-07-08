"""Partition layout diagnostics."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from lakehouse_doctor.models import Finding, ScanConfig


def _partition_key_value(part: str) -> tuple[str, str] | None:
    if "=" not in part:
        return None
    key, value = part.split("=", 1)
    if not key or not value:
        return None
    return key, value


def check_partition_skew(root: Path, files: list[Path], config: ScanConfig) -> list[Finding]:
    sizes: dict[tuple[str, str], int] = defaultdict(int)

    for file_path in files:
        relative = file_path.relative_to(root)
        for part in relative.parts[:-1]:
            partition = _partition_key_value(part)
            if partition is None:
                continue
            sizes[partition] += file_path.stat().st_size

    if len(sizes) < 2:
        return []

    non_zero = [size for size in sizes.values() if size > 0]
    if not non_zero:
        return []

    largest = max(non_zero)
    smallest = min(non_zero)
    if smallest == 0 or largest / smallest < config.partition_skew_ratio:
        return []

    return [
        Finding(
            code="PARTITION_SKEW",
            severity="warn",
            path=str(root),
            message="Partition sizes are uneven",
            metadata={
                "largest_bytes": largest,
                "smallest_bytes": smallest,
                "ratio": round(largest / smallest, 2),
            },
        )
    ]
