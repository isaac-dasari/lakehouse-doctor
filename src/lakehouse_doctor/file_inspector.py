"""Helpers for inspecting local data files."""

from __future__ import annotations

import csv
from pathlib import Path

SUPPORTED_EXTENSIONS = {".csv", ".json", ".jsonl", ".parquet"}
CSV_EXTENSIONS = {".csv"}


def is_data_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def is_csv_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in CSV_EXTENSIONS


def read_csv_header(path: Path) -> tuple[str, ...]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            return tuple(next(reader))
        except StopIteration:
            return ()


def iter_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def table_name_for_file(root: Path, file_path: Path) -> str:
    relative = file_path.relative_to(root)
    if len(relative.parts) == 1:
        return root.name
    return relative.parts[0]
