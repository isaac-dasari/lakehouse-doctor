"""HTML report rendering."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any


def write_html_report(payload: dict[str, Any], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    findings = payload.get("findings", [])
    severity_counts = payload.get("severity_counts", {})
    rows = "\n".join(_finding_row(item) for item in findings) or (
        '<tr><td colspan="4">No findings detected.</td></tr>'
    )
    format_rows = "\n".join(
        f"<tr><td>{escape(str(fmt))}</td><td>{count}</td></tr>"
        for fmt, count in sorted(payload.get("format_counts", {}).items())
    ) or '<tr><td colspan="2">No data files detected.</td></tr>'

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lakehouse Doctor Report</title>
  <style>
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0f172a; color: #e2e8f0; }}
    header {{ padding: 32px; background: linear-gradient(135deg, #111827, #1e293b); border-bottom: 1px solid #334155; }}
    h1 {{ margin: 0 0 8px 0; font-size: 32px; }}
    p {{ color: #94a3b8; }}
    main {{ padding: 32px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 28px; }}
    .card {{ background: #111827; border: 1px solid #334155; border-radius: 14px; padding: 18px; }}
    .metric {{ font-size: 28px; font-weight: 800; color: #f8fafc; }}
    .label {{ color: #94a3b8; font-size: 13px; margin-top: 4px; }}
    table {{ width: 100%; border-collapse: collapse; background: #111827; border: 1px solid #334155; border-radius: 14px; overflow: hidden; margin-bottom: 28px; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #1f2937; text-align: left; vertical-align: top; font-size: 14px; }}
    th {{ background: #1e293b; color: #cbd5e1; }}
    tr:last-child td {{ border-bottom: none; }}
    .error {{ color: #fca5a5; font-weight: 700; }}
    .warn {{ color: #fde68a; font-weight: 700; }}
    .info {{ color: #93c5fd; font-weight: 700; }}
    .section-title {{ margin: 0 0 16px 0; font-size: 22px; }}
  </style>
</head>
<body>
  <header>
    <h1>Lakehouse Doctor Report</h1>
    <p>Local health diagnostics for lakehouse-style datasets.</p>
  </header>
  <main>
    <section class="cards">
      <div class="card"><div class="metric">{payload.get('table_count', 0)}</div><div class="label">Tables</div></div>
      <div class="card"><div class="metric">{payload.get('file_count', 0)}</div><div class="label">Files</div></div>
      <div class="card"><div class="metric">{payload.get('total_bytes', 0)}</div><div class="label">Bytes</div></div>
      <div class="card"><div class="metric">{len(findings)}</div><div class="label">Findings</div></div>
      <div class="card"><div class="metric">{severity_counts.get('error', 0)}</div><div class="label">Errors</div></div>
      <div class="card"><div class="metric">{severity_counts.get('warn', 0)}</div><div class="label">Warnings</div></div>
    </section>

    <section>
      <h2 class="section-title">Formats</h2>
      <table><thead><tr><th>Format</th><th>Files</th></tr></thead><tbody>{format_rows}</tbody></table>
    </section>

    <section>
      <h2 class="section-title">Findings</h2>
      <table>
        <thead><tr><th>Severity</th><th>Code</th><th>Path</th><th>Message</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""
    output.write_text(page, encoding="utf-8")
    return output


def _finding_row(item: dict[str, Any]) -> str:
    severity = escape(str(item.get("severity", "")))
    return (
        "<tr>"
        f"<td class=\"{severity}\">{severity}</td>"
        f"<td>{escape(str(item.get('code', '')))}</td>"
        f"<td>{escape(str(item.get('path', '')))}</td>"
        f"<td>{escape(str(item.get('message', '')))}</td>"
        "</tr>"
    )
