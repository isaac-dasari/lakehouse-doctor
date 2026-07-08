"""Local lakehouse scanner."""

from __future__ import annotations

from pathlib import Path

from lakehouse_doctor.file_inspector import is_data_file
from lakehouse_doctor.models import ScanConfig, ScanResult
from lakehouse_doctor.rules.duplicates import check_duplicate_keys
from lakehouse_doctor.rules.file_size import check_file_sizes
from lakehouse_doctor.rules.freshness import check_freshness
from lakehouse_doctor.rules.partitions import check_partition_skew
from lakehouse_doctor.rules.schema import check_schema_drift


def _data_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if is_data_file(path))


def _table_count(root: Path, files: list[Path]) -> int:
    tables = set()
    for file_path in files:
        relative = file_path.relative_to(root)
        tables.add(root.name if len(relative.parts) == 1 else relative.parts[0])
    return len(tables)


def scan_lakehouse(config: ScanConfig | Path | str) -> ScanResult:
    if not isinstance(config, ScanConfig):
        config = ScanConfig(root_path=Path(config))

    root = config.root_path
    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    files = _data_files(root)
    findings = []
    findings.extend(check_file_sizes(root, files, config))
    findings.extend(check_schema_drift(root, files))
    findings.extend(check_partition_skew(root, files, config))
    findings.extend(check_freshness(root, files, config))
    findings.extend(check_duplicate_keys(root, files, config))

    return ScanResult(
        root_path=str(root),
        table_count=_table_count(root, files),
        file_count=len(files),
        total_bytes=sum(path.stat().st_size for path in files),
        findings=findings,
    )
