"""Command line interface."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from lakehouse_doctor.models import ScanConfig
from lakehouse_doctor.scanner import scan_lakehouse

app = typer.Typer(help="Lakehouse Doctor: local diagnostics for lakehouse folders")
console = Console()
DEFAULT_OUTPUT = Path(".lakehouse-doctor/report.json")
DEFAULT_HTML = Path(".lakehouse-doctor/report.html")


@app.command()
def scan(
    path: Path,
    output: Path = typer.Option(DEFAULT_OUTPUT, "--output", "-o"),
    primary_key: str | None = typer.Option(None, "--primary-key"),
    freshness_days: int = typer.Option(30, "--freshness-days"),
    small_file_threshold_kb: int = typer.Option(128, "--small-file-threshold-kb"),
) -> None:
    """Scan a local lakehouse folder."""

    config = ScanConfig(
        root_path=path,
        primary_key=primary_key,
        freshness_days=freshness_days,
        small_file_threshold_bytes=small_file_threshold_kb * 1024,
    )
    result = scan_lakehouse(config)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

    console.print(f"Scanned {result.table_count} tables and {result.file_count} files")
    console.print(f"Findings: {len(result.findings)}")
    console.print(f"Report written to {output}")


@app.command()
def report(
    input_path: Path = typer.Option(DEFAULT_OUTPUT, "--input", "-i"),
    html: bool = typer.Option(False, "--html"),
    output: Path = typer.Option(DEFAULT_HTML, "--output", "-o"),
) -> None:
    """Print the latest scan report."""

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    findings = payload.get("findings", [])

    console.print("[bold]Lakehouse Doctor Report[/bold]")
    console.print(f"Tables: {payload.get('table_count', 0)}")
    console.print(f"Files: {payload.get('file_count', 0)}")
    console.print(f"Bytes: {payload.get('total_bytes', 0)}")
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
        output.parent.mkdir(parents=True, exist_ok=True)
        rows = "".join(
            "<tr>"
            f"<td>{item.get('severity', '')}</td>"
            f"<td>{item.get('code', '')}</td>"
            f"<td>{item.get('path', '')}</td>"
            f"<td>{item.get('message', '')}</td>"
            "</tr>"
            for item in findings
        )
        page = f"""<!doctype html>
<html lang=\"en\">
<head><meta charset=\"utf-8\"><title>Lakehouse Doctor Report</title></head>
<body>
<h1>Lakehouse Doctor Report</h1>
<p>Tables: {payload.get('table_count', 0)}</p>
<p>Files: {payload.get('file_count', 0)}</p>
<p>Findings: {len(findings)}</p>
<table border=\"1\" cellpadding=\"6\" cellspacing=\"0\">
<tr><th>Severity</th><th>Code</th><th>Path</th><th>Message</th></tr>
{rows}
</table>
</body>
</html>
"""
        output.write_text(page, encoding="utf-8")
        console.print(f"HTML report written to {output}")


@app.command()
def rules() -> None:
    """List built-in rules."""

    table = Table(title="Built-in rules")
    table.add_column("Code")
    table.add_column("Description")
    table.add_row("SMALL_FILES", "Detects many files below the configured size threshold")
    table.add_row("SCHEMA_DRIFT", "Detects multiple CSV schemas within the same table")
    table.add_row("PARTITION_SKEW", "Detects uneven partition sizes")
    table.add_row("STALE_TABLE", "Detects data older than the freshness threshold")
    table.add_row("DUPLICATE_KEYS", "Detects duplicate primary key values in CSV files")
    console.print(table)
