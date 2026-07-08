# Lakehouse Doctor

Local-first health checks and diagnostics for lakehouse-style data folders.

Lakehouse Doctor scans local table folders and reports practical reliability and performance risks: small files, schema drift, partition skew, stale data, and duplicate keys.

## Why this exists

Data platforms often fail slowly before they fail loudly. Tables accumulate tiny files, partitions become uneven, schemas drift across producers, and stale datasets continue to feed downstream jobs.

Lakehouse Doctor gives engineers a fast local workflow for checking table health before adding heavier platform integrations.

## Current MVP

- Local folder scanner
- CSV schema inspection
- Small-file detection
- Partition skew detection for `key=value` folder layouts
- Freshness checks
- Duplicate key checks for CSV data
- JSON summary output
- HTML report output
- CLI workflow
- Example lakehouse folder
- Test suite and CI

## Install locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## 60-second demo

```bash
lakehouse-doctor scan examples/sample_lakehouse --primary-key order_id
lakehouse-doctor report --html
lakehouse-doctor rules
```

The default scan writes:

```text
.lakehouse-doctor/report.json
```

The HTML report writes:

```text
.lakehouse-doctor/report.html
```

## CLI

```bash
lakehouse-doctor scan <path>
lakehouse-doctor scan <path> --primary-key order_id
lakehouse-doctor scan <path> --freshness-days 7
lakehouse-doctor report
lakehouse-doctor report --html
lakehouse-doctor rules
```

## Example finding

```text
WARN SMALL_FILES examples/sample_lakehouse/orders
5 files are below 128.0 KB
```

## Who this is for

Lakehouse Doctor is for data engineers, platform engineers, and analytics engineers who maintain data lake and lakehouse tables and need a quick local diagnostic pass.

## Roadmap

- Parquet metadata inspection
- Delta Lake support
- Apache Iceberg support
- AWS Glue catalog integration
- S3 scanning
- OpenLineage export
- CI quality gates
- Historical trend comparison

## Design principles

- Local-first by default
- Fast feedback
- Clear findings over noisy metrics
- Useful without a hosted service
- Simple enough to run in CI

## License

MIT
