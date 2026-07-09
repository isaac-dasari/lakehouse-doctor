from typer.testing import CliRunner

from lakehouse_doctor.cli import app

runner = CliRunner()


def test_rules_command() -> None:
    result = runner.invoke(app, ["rules"])

    assert result.exit_code == 0
    assert "SMALL_FILES" in result.output
    assert "SCHEMA_DRIFT" in result.output
    assert "PARQUET_READ_ERROR" in result.output


def test_scan_report_check_and_compare_commands(tmp_path) -> None:
    report_path = tmp_path / "report.json"
    html_path = tmp_path / "report.html"
    latest_path = tmp_path / "latest.json"

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

    report_result = runner.invoke(
        app,
        ["report", "--input", str(report_path), "--html", "--output", str(html_path)],
    )
    assert report_result.exit_code == 0
    assert html_path.exists()
    assert "Lakehouse Doctor Report" in html_path.read_text(encoding="utf-8")

    check_result = runner.invoke(app, ["check", "--input", str(report_path), "--fail-on", "critical"])
    assert check_result.exit_code == 0

    latest_path.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")
    compare_result = runner.invoke(app, ["compare", str(report_path), str(latest_path)])
    assert compare_result.exit_code == 0
    assert "file_count_delta" in compare_result.output
