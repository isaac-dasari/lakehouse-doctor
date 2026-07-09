"""Parquet metadata diagnostics."""

from __future__ import annotations

from pathlib import Path

from lakehouse_doctor.file_inspector import is_parquet_file, parquet_metadata, table_name_for_file
from lakehouse_doctor.models import Finding


def check_parquet_metadata(root: Path, files: list[Path]) -> list[Finding]:
    findings: list[Finding] = []

    for path in files:
        if not is_parquet_file(path):
            continue
        try:
            metadata = parquet_metadata(path)
        except Exception as exc:  # pragma: no cover - defensive guard for corrupt files
            findings.append(
                Finding(
                    code="PARQUET_READ_ERROR",
                    severity="error",
                    path=str(path),
                    message="Parquet metadata could not be read",
                    metadata={"error": repr(exc)},
                )
            )
            continue

        if metadata["row_count"] == 0:
            findings.append(
                Finding(
                    code="EMPTY_PARQUET_FILE",
                    severity="warn",
                    path=str(path),
                    message="Parquet file has zero rows",
                    metadata={"table": table_name_for_file(root, path), **metadata},
                )
            )

        if metadata["row_group_count"] > 50:
            findings.append(
                Finding(
                    code="MANY_ROW_GROUPS",
                    severity="warn",
                    path=str(path),
                    message="Parquet file has many row groups for a single file",
                    metadata={"table": table_name_for_file(root, path), **metadata},
                )
            )

    return findings
