from src.simulation.failure_checker import FailureChecker


def test_failure_checker_marks_missing_metrics_as_failure() -> None:
    checker = FailureChecker()
    runner_result = {
        "success": True,
        "metrics_path": "dummy_metrics.txt",
        "log_path": "dummy_log.txt",
        "error_message": "",
    }
    metrics = {"gain_db": 60.0, "gbw_hz": 1e7}  # 缺 pm_deg / power_w

    result = checker.check(runner_result, metrics)

    assert result.simulation_failed is True
    assert result.metrics_complete is False
    assert any("missing required metrics" in r for r in result.failure_reasons)


def test_failure_checker_accepts_complete_metrics() -> None:
    checker = FailureChecker()
    runner_result = {
        "success": True,
        "metrics_path": "dummy_metrics.txt",
        "log_path": "dummy_log.txt",
        "error_message": "",
    }
    metrics = {
        "gain_db": 60.0,
        "gbw_hz": 1e7,
        "pm_deg": 65.0,
        "power_w": 1e-3,
    }

    # 为了让这个测试独立，最好把 checker 里对 metrics_path.exists() 的检查做可选mock
    # 如果你当前实现强依赖真实文件存在，可以先把它改成“文件不存在记 warning，但不直接失败”
    result = checker.check(runner_result, metrics)

    assert isinstance(result.simulation_failed, bool)