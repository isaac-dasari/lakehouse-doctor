from pathlib import Path

from lakehouse_doctor.models import ScanConfig
from lakehouse_doctor.scanner import scan_lakehouse


def test_scan_detects_expected_findings() -> None:
    result = scan_lakehouse(
        ScanConfig(root_path=Path("examples/sample_lakehouse"), primary_key="order_id")
    )
    codes = {finding.code for finding in result.findings}

    assert result.table_count == 2
    assert result.file_count == 6
    assert result.format_counts == {"csv": 6}
    assert "SMALL_FILES" in codes
    assert "SCHEMA_DRIFT" in codes
    assert "DUPLICATE_KEYS" in codes


def test_scan_accepts_path_input() -> None:
    result = scan_lakehouse("examples/sample_lakehouse")

    assert result.file_count == 6
    assert result.total_bytes > 0
    assert result.severity_counts()["warn"] >= 1
