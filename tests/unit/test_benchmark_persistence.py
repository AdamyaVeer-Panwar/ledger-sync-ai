from evaluation.benchmark_llm import (
    BenchmarkResult,
    load_completed_results,
    persist_result,
)


def test_persist_and_load_result(tmp_path, monkeypatch):
    results_dir = tmp_path / "results"
    results_file = (
        results_dir / "llm_baseline_results.jsonl"
    )

    monkeypatch.setattr(
        "evaluation.benchmark_llm.RESULTS_DIR",
        results_dir,
    )

    monkeypatch.setattr(
        "evaluation.benchmark_llm.RESULTS_FILE",
        results_file,
    )

    result = BenchmarkResult(
        settlement_id="S001",
        expected=["L001"],
        decision="MATCH",
        candidate_ids=["L001"],
        confidence=0.97,
        candidate_count=3,
        latency_seconds=0.42,
        input_tokens=500,
        output_tokens=40,
        total_tokens=540,
    )

    persist_result(result)

    assert results_file.exists()

    loaded = load_completed_results()

    assert "S001" in loaded

    restored = loaded["S001"]

    assert restored.settlement_id == "S001"
    assert restored.expected == ["L001"]
    assert restored.decision == "MATCH"
    assert restored.candidate_ids == ["L001"]
    assert restored.confidence == 0.97
    assert restored.candidate_count == 3
    assert restored.input_tokens == 500
    assert restored.output_tokens == 40
    assert restored.total_tokens == 540


def test_load_completed_results_returns_empty_when_file_missing(
    tmp_path,
    monkeypatch,
):
    results_file = tmp_path / "missing.jsonl"

    monkeypatch.setattr(
        "evaluation.benchmark_llm.RESULTS_FILE",
        results_file,
    )

    loaded = load_completed_results()

    assert loaded == {}


def test_load_completed_results_skips_malformed_lines(
    tmp_path,
    monkeypatch,
):
    results_file = tmp_path / "results.jsonl"

    results_file.write_text(
        """
        not-valid-json

        {"settlement_id":"S002","expected":null,"decision":"NO_MATCH","candidate_ids":[],"confidence":0.1,"candidate_count":0,"latency_seconds":0.2,"input_tokens":10,"output_tokens":5,"total_tokens":15,"error_type":null,"error_message":null}
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "evaluation.benchmark_llm.RESULTS_FILE",
        results_file,
    )

    loaded = load_completed_results()

    assert list(loaded.keys()) == ["S002"]
    assert loaded["S002"].decision == "NO_MATCH"
    assert loaded["S002"].candidate_ids == []