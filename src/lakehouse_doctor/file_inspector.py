"""Helpers for inspecting local data files."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

SUPPORTED_EXTENSIONS = {".csv", ".json", ".jsonl", ".parquet"}
CSV_EXTENSIONS = {".csv"}
PARQUET_EXTENSIONS = {".parquet"}


def is_data_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def is_csv_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in CSV_EXTENSIONS


def is_parquet_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in PARQUET_EXTENSIONS


def file_format(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    return suffix or "unknown"


def read_csv_header(path: Path) -> tuple[str, ...]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            return tuple(next(reader))
        except StopIteration:
            return ()


def read_parquet_schema(path: Path) -> tuple[str, ...]:
    parquet_file = pq.ParquetFile(path)
    return tuple(parquet_file.schema_arrow.names)


def read_schema(path: Path) -> tuple[str, ...]:
    if is_csv_file(path):
        return read_csv_header(path)
    if is_parquet_file(path):
        return read_parquet_schema(path)
    return ()


def parquet_metadata(path: Path) -> dict[str, Any]:
    parquet_file = pq.ParquetFile(path)
    metadata = parquet_file.metadata
    return {
        "row_count": metadata.num_rows,
        "row_group_count": metadata.num_row_groups,
        "schema": list(parquet_file.schema_arrow.names),
    }


def iter_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def iter_parquet_rows(path: Path) -> list[dict[str, object]]:
    table = pq.read_table(path)
    return table.to_pylist()


def iter_rows(path: Path) -> list[dict[str, object]]:
    if is_csv_file(path):
        return list(iter_csv_rows(path))
    if is_parquet_file(path):
        return iter_parquet_rows(path)
    return []


def table_name_for_file(root: Path, file_path: Path) -> str:
    relative = file_path.relative_to(root)
    if len(relative.parts) == 1:
        return root.name
    return relative.parts[0]
