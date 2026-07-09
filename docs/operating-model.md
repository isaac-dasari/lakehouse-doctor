# Operating Model

Lakehouse Doctor is built for three operating modes.

## 1. Local developer check

A data engineer can run a scan before committing a pipeline, table layout, or fixture change.

```bash
lakehouse-doctor scan ./data --primary-key order_id
lakehouse-doctor report --html
```

## 2. CI quality gate

A repository can fail a pull request when selected severities are present.

```bash
lakehouse-doctor scan ./data --primary-key order_id --output report.json
lakehouse-doctor check --input report.json --fail-on error
```

## 3. Trend comparison

A team can compare two scan reports to detect whether a change introduced new findings, increased file count, or changed data volume.

```bash
lakehouse-doctor compare baseline.json latest.json --fail-on-new-error
```

## Recommended workflow

1. Generate a baseline report from a known-good fixture or table snapshot.
2. Run a latest report after a code, config, schema, or partition-layout change.
3. Compare baseline and latest reports.
4. Fail CI only on severities that the team has agreed to enforce.

## Production limitations

Lakehouse Doctor is local-first. It does not replace a full metadata catalog, table optimizer, distributed profiler, or enterprise data observability platform. Its purpose is fast feedback for common layout, schema, freshness, duplicate-key, and Parquet metadata risks.
