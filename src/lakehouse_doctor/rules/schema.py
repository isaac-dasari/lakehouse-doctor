"""Schema diagnostics for CSV files."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from lakehouse_doctor.file_inspector import is_csv_file, read_csv_header, table_name_for_file
from lakehouse_doctor.models import Finding


def check_schema_drift(root: Path, files: list[Path]) -> list[Finding]:
    schemas_by_table: dict[str, dict[tuple[str, ...], list[str]]] = defaultdict(lambda: defaultdict(list))

    for path in files:
        if not is_csv_file(path):
            continue
        table = table_name_for_file(root, path)
        header = read_csv_header(path)
        schemas_by_table[table][header].append(str(path))

    findings: list[Finding] = []
    for table, schemas in schemas_by_table.items():
        if len(schemas) <= 1:
            continue
        findings.append(
            Finding(
                code="SCHEMA_DRIFT",
                severity="error",
                path=str(root / table),
                message=f"{table} has {len(schemas)} distinct CSV schemas",
                metadata={"schema_count": len(schemas), "schemas": [list(schema) for schema in schemas]},
            )
        )

    return findings
