# Built-in Rules

Lakehouse Doctor is intentionally rule-based. Each rule is designed to be understandable in a pull request, CI job, or local terminal session.

## SMALL_FILES

Detects many files below the configured size threshold. Small files can increase planning overhead, metadata pressure, and distributed-processing inefficiency.

Default threshold: `128 KB`  
Default minimum count: `5`

## SCHEMA_DRIFT

Detects multiple schemas within the same table folder. It supports CSV headers and Parquet metadata schemas.

This is useful when multiple producers write to the same logical table or when a schema rollout happens without downstream coordination.

## PARTITION_SKEW

Detects uneven partition sizes for `key=value` folder layouts.

Example:

```text
orders/dt=2026-07-01/part-000.parquet
orders/dt=2026-07-02/part-000.parquet
```

## STALE_TABLE

Detects tables where the newest data file is older than the configured freshness threshold.

Default threshold: `30 days`

## DUPLICATE_KEYS

Detects duplicate values for a configured primary key across CSV and Parquet files.

Example:

```bash
lakehouse-doctor scan ./data --primary-key order_id
```

## PARQUET_READ_ERROR

Detects Parquet files whose metadata cannot be read. This can indicate corruption, partial writes, or non-Parquet files with the wrong extension.

## EMPTY_PARQUET_FILE

Detects Parquet files with zero rows.

## MANY_ROW_GROUPS

Detects Parquet files with many row groups. This can be a signal to review write settings and compaction behavior.

## CI quality gates

Fail on errors only:

```bash
lakehouse-doctor check --input report.json --fail-on error
```

Fail on warnings and errors:

```bash
lakehouse-doctor check --input report.json --fail-on warn,error
```
