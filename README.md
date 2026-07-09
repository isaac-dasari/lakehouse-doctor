# Lakehouse Doctor

Local-first health checks and diagnostics for lakehouse-style data folders.

Lakehouse Doctor scans local table folders and reports practical reliability and performance risks: small files, schema drift, partition skew, stale data, duplicate keys, and Parquet metadata issues.

## Why this exists

Data platforms often fail slowly before they fail loudly. Tables accumulate tiny files, partitions become uneven, schemas drift across producers, stale datasets continue to feed downstream jobs, and Parquet layout problems hide until query engines become slow or unreliable.

Lakehouse Doctor gives engineers a fast local workflow for checking table health before adding heavier platform integrations.

## Current MVP

- Local folder scanner
- CSV and Parquet schema inspection
- Parquet metadata inspection
- Small-file detection
- Partition skew detection for `key=value` folder layouts
- Freshness checks
- Duplicate key checks for CSV and Parquet data
- JSON summary output
- Polished HTML report output
- CI quality gate command
- Baseline-vs-latest report comparison
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

## CI quality gate

Fail only on errors:

```bash
lakehouse-doctor scan examples/sample_lakehouse --primary-key order_id --output report.json
lakehouse-doctor check --input report.json --fail-on error
```

Fail on warnings and errors:

```bash
lakehouse-doctor check --input report.json --fail-on warn,error
```

You can also fail directly during scan:

```bash
lakehouse-doctor scan examples/sample_lakehouse --primary-key order_id --fail-on error
```

## Compare two reports

```bash
lakehouse-doctor compare baseline.json latest.json
lakehouse-doctor compare baseline.json latest.json --fail-on-new-error
```

Comparison output includes table-count delta, file-count delta, byte delta, finding-count delta, severity deltas, new findings, and resolved findings.

## CLI

```bash
lakehouse-doctor scan <path>
lakehouse-doctor scan <path> --primary-key order_id
lakehouse-doctor scan <path> --freshness-days 7
lakehouse-doctor scan <path> --fail-on error
lakehouse-doctor check --input report.json --fail-on error
lakehouse-doctor report
lakehouse-doctor report --html
lakehouse-doctor compare baseline.json latest.json
lakehouse-doctor rules
```

## Example finding

```text
WARN SMALL_FILES examples/sample_lakehouse/orders
5 files are below 128.0 KB
```

## Who this is for

Lakehouse Doctor is for data engineers, platform engineers, and analytics engineers who maintain data lake and lakehouse tables and need a quick local diagnostic pass before pipeline changes reach production.

## What this does not solve

Lakehouse Doctor is not a full metadata catalog, query optimizer, distributed profiler, object-store crawler, or enterprise data observability platform. It is a lightweight local diagnostic tool for common layout, schema, freshness, duplicate-key, and Parquet metadata risks.

## Roadmap

- S3 and MinIO scanning
- Delta Lake support
- Apache Iceberg support
- AWS Glue catalog integration
- OpenLineage export
- Stored historical trend database
- GitHub PR comment integration

## Design principles

- Local-first by default
- Fast feedback
- Clear findings over noisy metrics
- Useful without a hosted service
- Simple enough to run in CI
- Honest limitations over inflated claims

## License

MIT
