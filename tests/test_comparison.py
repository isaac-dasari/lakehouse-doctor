import json

from typer.testing import CliRunner

from lakehouse_doctor.cli import app
from lakehouse_doctor.comparison import compare_reports, should_fail_gate

runner = CliRunner()


def test_compare_reports_detects_new_findings(tmp_path):
    baseline = tmp_path / "baseline.json"
    latest = tmp_path / "latest.json"
    baseline.write_text(
        json.dumps({"table_count": 1, "file_count": 1, "total_bytes": 10, "findings": []}),
        encoding="utf-8",
    )
    latest.write_text(
        json.dumps(
            {
                "table_count": 1,
                "file_count": 2,
                "total_bytes": 20,
                "findings": [
                    {
                        "severity": "error",
                        "code": "SCHEMA_DRIFT",
                        "path": "orders",
                        "message": "schema drift",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = compare_reports(baseline, latest)

    assert result["file_count_delta"] == 1
    assert result["severity_delta"]["error"] == 1
    assert result["new_findings"]


def test_quality_gate() -> None:
    report = {"findings": [{"severity": "warn"}]}

    assert should_fail_gate(report, {"warn"})
    assert not should_fail_gate(report, {"error"})


def test_check_command_fails_on_error(tmp_path):
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps({"findings": [{"severity": "error", "code": "X"}]}),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check", "--input", str(report), "--fail-on", "error"])

    assert result.exit_code == 1
