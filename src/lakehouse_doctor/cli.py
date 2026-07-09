"""Command line interface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from lakehouse_doctor.comparison import compare_reports, load_report, should_fail_gate
from lakehouse_doctor.html_report import write_html_report
from lakehouse_doctor.models import ScanConfig
from lakehouse_doctor.scanner import scan_lakehouse

app = typer.Typer(help="Lakehouse Doctor: local diagnostics for lakehouse folders")
console = Console()
DEFAULT_OUTPUT = Path(".lakehouse-doctor/report.json")
DEFAULT_HTML = Path(".lakehouse-doctor/report.html")


@app.command()
def scan(
    path: Path,
    output: Annotated[Path, typer.Option("--output", "-o")] = DEFAULT_OUTPUT,
    primary_key: Annotated[str | None, typer.Option("--primary-key")] = None,
    freshness_days: Annotated[int, typer.Option("--freshness-days")] = 30,
    small_file_threshold_kb: Annotated[int, typer.Option("--small-file-threshold-kb")] = 128,
    fail_on: Annotated[str | None, typer.Option("--fail-on")] = None,
) -> None:
    """Scan a local lakehouse folder."""

    config = ScanConfig(
        root_path=path,
        primary_key=primary_key,
        freshness_days=freshness_days,
        small_file_threshold_bytes=small_file_threshold_kb * 1024,
    )
    result = scan_lakehouse(config)
    payload = result.to_dict()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    console.print(f"Scanned {result.table_count} tables and {result.file_count} files")
    console.print(f"Formats: {result.format_counts}")
    console.print(f"Findings: {len(result.findings)}")
    console.print(f"Report written to {output}")

    if fail_on and should_fail_gate(payload, _parse_fail_on(fail_on)):
        console.print(f"[red]Quality gate failed for severities: {fail_on}[/red]")
        raise typer.Exit(code=1)


@app.command()
def check(
    input_path: Annotated[Path, typer.Option("--input", "-i")] = DEFAULT_OUTPUT,
    fail_on: Annotated[str, typer.Option("--fail-on")] = "error",
) -> None:
    """Fail CI when a scan report contains selected severities."""

    payload = load_report(input_path)
    severities = _parse_fail_on(fail_on)
    if should_fail_gate(payload, severities):
        console.print(f"[red]Lakehouse quality gate failed: {fail_on} finding present[/red]")
        raise typer.Exit(code=1)
    console.print("[green]Lakehouse quality gate passed[/green]")


@app.command()
def report(
    input_path: Annotated[Path, typer.Option("--input", "-i")] = DEFAULT_OUTPUT,
    html: Annotated[bool, typer.Option("--html")] = False,
    output: Annotated[Path, typer.Option("--output", "-o")] = DEFAULT_HTML,
) -> None:
    """Print the latest scan report."""

    payload = load_report(input_path)
    findings = payload.get("findings", [])
    severity_counts = payload.get("severity_counts", {})

    console.print("[bold]Lakehouse Doctor Report[/bold]")
    console.print(f"Tables: {payload.get('table_count', 0)}")
    console.print(f"Files: {payload.get('file_count', 0)}")
    console.print(f"Bytes: {payload.get('total_bytes', 0)}")
    console.print(f"Formats: {payload.get('format_counts', {})}")
    console.print(f"Severity counts: {severity_counts}")
    console.print(f"Findings: {len(findings)}")

    table = Table(title="Findings")
    table.add_column("Severity")
    table.add_column("Code")
    table.add_column("Path")
    table.add_column("Message")
    for item in findings:
        table.add_row(
            str(item.get("severity", "")),
            str(item.get("code", "")),
            str(item.get("path", "")),
            str(item.get("message", "")),
        )
    if findings:
        console.print(table)

    if html:
        write_html_report(payload, output)
        console.print(f"HTML report written to {output}")


@app.command("compare")
def compare(
    baseline: Path,
    latest: Path,
    fail_on_new_error: Annotated[bool, typer.Option("--fail-on-new-error")] = False,
) -> None:
    """Compare two scan reports for trend and regression review."""

    result = compare_reports(baseline, latest)
    console.print_json(json.dumps(result))

    if fail_on_new_error and any(item.startswith("error|") for item in result["new_findings"]):
        console.print("[red]New error finding detected[/red]")
        raise typer.Exit(code=1)


@app.command()
def rules() -> None:
    """List built-in rules."""

    table = Table(title="Built-in rules")
    table.add_column("Code")
    table.add_column("Description")
    table.add_row("SMALL_FILES", "Detects many files below the configured size threshold")
    table.add_row("SCHEMA_DRIFT", "Detects multiple CSV or Parquet schemas within the same table")
    table.add_row("PARTITION_SKEW", "Detects uneven partition sizes")
    table.add_row("STALE_TABLE", "Detects data older than the freshness threshold")
    table.add_row("DUPLICATE_KEYS", "Detects duplicate primary key values in CSV or Parquet files")
    table.add_row("PARQUET_READ_ERROR", "Detects unreadable Parquet metadata")
    table.add_row("EMPTY_PARQUET_FILE", "Detects Parquet files with zero rows")
    table.add_row("MANY_ROW_GROUPS", "Detects Parquet files with many row groups")
    console.print(table)


def _parse_fail_on(value: str) -> set[str]:
    return {item.strip().lower() for item in value.split(",") if item.strip()}
