"""Duplicate key diagnostics for CSV and Parquet files."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from lakehouse_doctor.file_inspector import iter_rows, table_name_for_file
from lakehouse_doctor.models import Finding, ScanConfig


def check_duplicate_keys(root: Path, files: list[Path], config: ScanConfig) -> list[Finding]:
    if not config.primary_key:
        return []

    values_by_table: dict[str, list[str]] = {}
    for path in files:
        table = table_name_for_file(root, path)
        rows = iter_rows(path)
        for row in rows:
            value = row.get(config.primary_key)
            if value is not None and str(value):
                values_by_table.setdefault(table, []).append(str(value))

    findings: list[Finding] = []
    for table, values in values_by_table.items():
        counts = Counter(values)
        duplicates = {key: count for key, count in counts.items() if count > 1}
        if not duplicates:
            continue
        findings.append(
            Finding(
                code="DUPLICATE_KEYS",
                severity="error",
                path=str(root / table),
                message=f"{table} has {len(duplicates)} duplicate key values",
                metadata={"primary_key": config.primary_key, "duplicates": duplicates},
            )
        )

    return findings
