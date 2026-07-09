"""Schema diagnostics for CSV and Parquet files."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from lakehouse_doctor.file_inspector import read_schema, table_name_for_file
from lakehouse_doctor.models import Finding


def check_schema_drift(root: Path, files: list[Path]) -> list[Finding]:
    schemas_by_table: dict[str, dict[tuple[str, ...], list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for path in files:
        schema = read_schema(path)
        if not schema:
            continue
        table = table_name_for_file(root, path)
        schemas_by_table[table][schema].append(str(path))

    findings: list[Finding] = []
    for table, schemas in schemas_by_table.items():
        if len(schemas) <= 1:
            continue
        findings.append(
            Finding(
                code="SCHEMA_DRIFT",
                severity="error",
                path=str(root / table),
                message=f"{table} has {len(schemas)} distinct schemas across scanned files",
                metadata={
                    "schema_count": len(schemas),
                    "schemas": [list(schema) for schema in schemas],
                },
            )
        )

    return findings
