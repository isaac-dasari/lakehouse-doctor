# Architecture

Lakehouse Doctor is organized around a local scan pipeline that turns lakehouse-style folders into actionable findings, reports, and CI gates.

```text
local folder
  -> scanner
  -> file format inspection
  -> built-in rules
  -> findings
  -> JSON report
  -> text / HTML report
  -> CI gate or baseline comparison
```

## Scanner

The scanner walks a local folder and identifies supported data files. It currently supports:

- CSV
- JSON
- JSONL
- Parquet

For CSV files, Lakehouse Doctor reads headers and rows. For Parquet files, it reads metadata, schema, row count, row group count, and primary-key values through PyArrow.

## Rules

Rules are small functions that inspect the file set and return findings. The current rules cover:

- small files
- schema drift across CSV and Parquet files
- partition skew for `key=value` folder layouts
- freshness
- duplicate keys across CSV and Parquet files
- unreadable Parquet metadata
- empty Parquet files
- high row-group counts

## Reports

The CLI writes JSON reports for automation and renders HTML reports for local review. Reports include table count, file count, total bytes, format counts, severity counts, and finding details.

## CI gates

The `check` command fails when selected severities are present:

```bash
lakehouse-doctor check --input report.json --fail-on error
lakehouse-doctor check --input report.json --fail-on warn,error
```

## Baseline comparison

The `compare` command compares two scan reports and returns deltas for table count, file count, total bytes, finding count, severity count, new findings, and resolved findings.

## Extension points

Future integrations can add object storage scanning, catalog-aware table discovery, Iceberg/Delta metadata readers, OpenLineage export, and historical trend storage without changing the basic rule interface.
