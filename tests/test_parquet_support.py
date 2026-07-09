from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from lakehouse_doctor.models import ScanConfig
from lakehouse_doctor.scanner import scan_lakehouse


def test_parquet_schema_and_duplicates(tmp_path: Path) -> None:
    table_dir = tmp_path / "orders"
    table_dir.mkdir()
    pq.write_table(
        pa.table({"order_id": ["1", "1", "2"], "amount": [10.0, 10.0, 20.0]}),
        table_dir / "part-000.parquet",
    )
    pq.write_table(
        pa.table({"order_id": ["3"], "amount": [30.0], "status": ["new"]}),
        table_dir / "part-001.parquet",
    )

    result = scan_lakehouse(ScanConfig(root_path=tmp_path, primary_key="order_id"))
    codes = {finding.code for finding in result.findings}

    assert result.format_counts == {"parquet": 2}
    assert "SCHEMA_DRIFT" in codes
    assert "DUPLICATE_KEYS" in codes


def test_empty_parquet_file_detection(tmp_path: Path) -> None:
    table_dir = tmp_path / "empty_table"
    table_dir.mkdir()
    pq.write_table(pa.table({"id": pa.array([], type=pa.string())}), table_dir / "empty.parquet")

    result = scan_lakehouse(tmp_path)
    codes = {finding.code for finding in result.findings}

    assert "EMPTY_PARQUET_FILE" in codes
