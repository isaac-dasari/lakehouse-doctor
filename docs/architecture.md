# Architecture

Lakehouse Doctor is organized around a small local scan pipeline.

```text
local folder
  -> scanner
  -> built-in rules
  -> findings
  -> JSON report
  -> text or HTML report
```

## Scanner

The scanner walks a local folder and identifies supported data files. The MVP supports CSV, JSON, JSONL, and Parquet file detection. CSV files receive deeper checks because headers and rows can be inspected without extra dependencies.

## Rules

Rules are small functions that inspect the file set and return findings. The current rules cover file size, schema drift, partition skew, freshness, and duplicate keys.

## Reports

The CLI writes a JSON report for automation and can render a simple HTML report for review.

## Extension points

Future integrations can add catalog-aware scanners, object storage support, table format metadata, and historical trend comparison without changing the rule interface.
