"""Compare Lakehouse Doctor scan reports."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_report(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compare_reports(baseline_path: Path | str, latest_path: Path | str) -> dict[str, Any]:
    baseline = load_report(baseline_path)
    latest = load_report(latest_path)

    baseline_findings = _finding_keys(baseline)
    latest_findings = _finding_keys(latest)

    return {
        "baseline": str(baseline_path),
        "latest": str(latest_path),
        "table_count_delta": latest.get("table_count", 0) - baseline.get("table_count", 0),
        "file_count_delta": latest.get("file_count", 0) - baseline.get("file_count", 0),
        "total_bytes_delta": latest.get("total_bytes", 0) - baseline.get("total_bytes", 0),
        "finding_count_delta": len(latest.get("findings", [])) - len(baseline.get("findings", [])),
        "severity_delta": _counter_delta(
            Counter(item.get("severity", "") for item in baseline.get("findings", [])),
            Counter(item.get("severity", "") for item in latest.get("findings", [])),
        ),
        "new_findings": sorted(latest_findings - baseline_findings),
        "resolved_findings": sorted(baseline_findings - latest_findings),
    }


def should_fail_gate(report: dict[str, Any], fail_on: set[str]) -> bool:
    severities = {str(item.get("severity", "")) for item in report.get("findings", [])}
    return bool(severities & fail_on)


def _finding_keys(report: dict[str, Any]) -> set[str]:
    keys = set()
    for finding in report.get("findings", []):
        keys.add(
            "|".join(
                [
                    str(finding.get("severity", "")),
                    str(finding.get("code", "")),
                    str(finding.get("path", "")),
                    str(finding.get("message", "")),
                ]
            )
        )
    return keys


def _counter_delta(baseline: Counter[str], latest: Counter[str]) -> dict[str, int]:
    severities = set(baseline) | set(latest)
    return {severity: latest.get(severity, 0) - baseline.get(severity, 0) for severity in sorted(severities)}
