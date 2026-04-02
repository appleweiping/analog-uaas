from pathlib import Path

from src.simulation.result_parser import ResultParser


def test_result_parser_reads_metrics_file(tmp_path: Path) -> None:
    metrics = tmp_path / "metrics.txt"
    metrics.write_text(
        "gain_db=62.5\n"
        "gbw_hz=12000000\n"
        "pm_deg=67.0\n"
        "power_w=0.0009\n",
        encoding="utf-8",
    )

    parser = ResultParser()
    result = parser.parse(metrics)

    assert result["gain_db"] == 62.5
    assert result["gbw_hz"] == 12000000.0
    assert result["pm_deg"] == 67.0
    assert result["power_w"] == 0.0009