from typer.testing import CliRunner

from lakehouse_doctor.cli import app

runner = CliRunner()


def test_rules_command() -> None:
    result = runner.invoke(app, ["rules"])

    assert result.exit_code == 0
    assert "SMALL_FILES" in result.output
    assert "SCHEMA_DRIFT" in result.output


def test_scan_and_report_commands(tmp_path) -> None:
    report_path = tmp_path / "report.json"
    html_path = tmp_path / "report.html"

    scan_result = runner.invoke(
        app,
        [
            "scan",
            "examples/sample_lakehouse",
            "--primary-key",
            "order_id",
            "--output",
            str(report_path),
        ],
    )
    assert scan_result.exit_code == 0
    assert report_path.exists()

    report_result = runner.invoke(app, ["report", "--input", str(report_path), "--html", "--output", str(html_path)])
    assert report_result.exit_code == 0
    assert html_path.exists()
    assert "Lakehouse Doctor Report" in html_path.read_text(encoding="utf-8")
