from __future__ import annotations

from evaluation.evaluator import (
    HYBRID_RESULTS_FILE,
    LLM_RESULTS_FILE,
    RULES_RESULTS_FILE,
    evaluate_system,
    hybrid_llm_invocation_count,
    load_all_inputs,
    llm_usage,
)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def pct(value: float) -> str:
    return f"{value:.2%}"


def ms(value: float) -> str:
    return f"{value * 1000:.2f} ms"


def delta_pct(after: float, before: float) -> str:
    return f"{after - before:+.2%}"


# ---------------------------------------------------------------------------
# Overall comparison
# ---------------------------------------------------------------------------

def print_system_report(
    name: str,
    report,
) -> None:
    metrics = report.overall

    print(
        f"{name:<10}"
        f"{pct(metrics.accuracy):>11}"
        f"{pct(metrics.precision):>12}"
        f"{pct(metrics.recall):>10}"
        f"{pct(metrics.false_match_rate):>13}"
        f"{pct(metrics.exception_rate):>12}"
        f"{pct(metrics.automation_rate):>12}"
        f"{ms(metrics.p95_latency_seconds):>14}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # -----------------------------------------------------------------------
    # Load + validate all benchmark artifacts.
    # -----------------------------------------------------------------------

    data = load_all_inputs()

    ground_truth = data["ground_truth"]
    scenarios = data["scenarios"]

    rules = data["rules"]
    llm = data["llm"]
    hybrid = data["hybrid"]

    raw_llm = data["raw_llm"]
    raw_hybrid = data["raw_hybrid"]

    # -----------------------------------------------------------------------
    # LLM usage
    # -----------------------------------------------------------------------

    (
        llm_input_tokens,
        llm_output_tokens,
        llm_total_tokens,
    ) = llm_usage(raw_llm)

    hybrid_invocation_count = (
        hybrid_llm_invocation_count(
            raw_hybrid
        )
    )

    # -----------------------------------------------------------------------
    # Hybrid token usage
    #
    # Hybrid JSONL currently does not persist per-record LLM token counts.
    #
    # Therefore estimate Hybrid token usage from the observed LLM-only
    # benchmark average.
    # -----------------------------------------------------------------------

    if raw_llm:
        average_input_tokens = (
            llm_input_tokens
            / len(raw_llm)
        )

        average_output_tokens = (
            llm_output_tokens
            / len(raw_llm)
        )

        average_total_tokens = (
            llm_total_tokens
            / len(raw_llm)
        )
    else:
        average_input_tokens = 0.0
        average_output_tokens = 0.0
        average_total_tokens = 0.0

    estimated_hybrid_input_tokens = int(
        round(
            hybrid_invocation_count
            * average_input_tokens
        )
    )

    estimated_hybrid_output_tokens = int(
        round(
            hybrid_invocation_count
            * average_output_tokens
        )
    )

    estimated_hybrid_total_tokens = int(
        round(
            hybrid_invocation_count
            * average_total_tokens
        )
    )

    # -----------------------------------------------------------------------
    # Evaluate Rules
    # -----------------------------------------------------------------------

    rules_report = evaluate_system(
        records=rules,
        scenarios=scenarios,
        llm_invocations=0,
    )

    # -----------------------------------------------------------------------
    # Evaluate LLM-only
    # -----------------------------------------------------------------------

    llm_report = evaluate_system(
        records=llm,
        scenarios=scenarios,
        llm_invocations=len(llm),
        input_tokens=llm_input_tokens,
        output_tokens=llm_output_tokens,
        total_tokens=llm_total_tokens,
    )

    # -----------------------------------------------------------------------
    # Evaluate Hybrid
    # -----------------------------------------------------------------------

    hybrid_report = evaluate_system(
        records=hybrid,
        scenarios=scenarios,
        llm_invocations=hybrid_invocation_count,
        input_tokens=estimated_hybrid_input_tokens,
        output_tokens=estimated_hybrid_output_tokens,
        total_tokens=estimated_hybrid_total_tokens,
        llm_invocations_by_settlement=(
            set(
                record["settlement_id"]
                for record in raw_hybrid
                if (
                    record.get("error_type") is None
                    and record.get("reason")
                    != "confident deterministic rule match"
                )
            )
        ),
    )

    # -----------------------------------------------------------------------
    # Header
    # -----------------------------------------------------------------------

    print()
    print("=" * 96)
    print(
        "LedgerSync AI — Day 8 Evaluation Report"
    )
    print("=" * 96)

    # -----------------------------------------------------------------------
    # Dataset
    # -----------------------------------------------------------------------

    print()
    print("Dataset")
    print("-------")

    print(
        f"Records              : "
        f"{len(ground_truth)}"
    )

    print(
        f"Scenarios            : "
        f"{len(set(scenarios.values()))}"
    )

    print(
        f"Rules results        : "
        f"{len(rules)}"
    )

    print(
        f"LLM results          : "
        f"{len(llm)}"
    )

    print(
        f"Hybrid results       : "
        f"{len(hybrid)}"
    )

    # -----------------------------------------------------------------------
    # Overall performance
    # -----------------------------------------------------------------------

    print()
    print("Overall Performance")
    print("-------------------")

    print(
        f"{'System':<10}"
        f"{'Accuracy':>11}"
        f"{'Precision':>12}"
        f"{'Recall':>10}"
        f"{'False-match':>13}"
        f"{'Exception':>12}"
        f"{'Automation':>12}"
        f"{'P95 latency':>14}"
    )

    print("-" * 96)

    print_system_report(
        "Rules",
        rules_report,
    )

    print_system_report(
        "LLM",
        llm_report,
    )

    print_system_report(
        "Hybrid",
        hybrid_report,
    )

    # -----------------------------------------------------------------------
    # Automation safety
    #
    # This is the most important new section for financial reconciliation.
    #
    # Automation rate tells us how much we automated.
    #
    # Correct automation rate tells us how much of the entire dataset
    # was both automated AND correct.
    #
    # Auto-match precision tells us how trustworthy automated matches are.
    #
    # False auto-match rate tells us how often we automated an incorrect
    # financial reconciliation.
    # -----------------------------------------------------------------------

    print()
    print("Automation Safety")
    print("------------------")

    print(
        f"{'System':<10}"
        f"{'Automation':>14}"
        f"{'Correct auto':>15}"
        f"{'Auto precision':>17}"
        f"{'False auto':>14}"
    )

    print("-" * 70)

    for name, report in (
        ("Rules", rules_report),
        ("LLM", llm_report),
        ("Hybrid", hybrid_report),
    ):
        metrics = report.overall

        print(
            f"{name:<10}"
            f"{pct(metrics.automation_rate):>14}"
            f"{pct(metrics.correct_automation_rate):>15}"
            f"{pct(metrics.auto_match_precision):>17}"
            f"{pct(metrics.false_auto_match_rate):>14}"
        )

    # -----------------------------------------------------------------------
    # Operational metrics
    # -----------------------------------------------------------------------

    print()
    print("Operational Metrics")
    print("-------------------")

    for name, report in (
        ("Rules", rules_report),
        ("LLM", llm_report),
        ("Hybrid", hybrid_report),
    ):
        metrics = report.overall

        print()
        print(name)

        print(
            f"  Automation rate      : "
            f"{pct(metrics.automation_rate)}"
        )

        print(
            f"  Correct automation   : "
            f"{pct(metrics.correct_automation_rate)}"
        )

        print(
            f"  Auto-match precision : "
            f"{pct(metrics.auto_match_precision)}"
        )

        print(
            f"  False auto-match     : "
            f"{pct(metrics.false_auto_match_rate)}"
        )

        print(
            f"  Exception rate       : "
            f"{pct(metrics.exception_rate)}"
        )

        print(
            f"  Failure rate         : "
            f"{pct(metrics.failure_rate)}"
        )

        print(
            f"  Throughput           : "
            f"{metrics.throughput_records_per_second:,.2f} "
            f"records/sec"
        )

        print(
            f"  Average latency      : "
            f"{ms(metrics.average_latency_seconds)}"
        )

        print(
            f"  P50 latency          : "
            f"{ms(metrics.p50_latency_seconds)}"
        )

        print(
            f"  P95 latency          : "
            f"{ms(metrics.p95_latency_seconds)}"
        )

        print(
            f"  LLM invocation rate  : "
            f"{pct(metrics.llm_invocation_rate)}"
        )

        print(
            f"  Input tokens         : "
            f"{metrics.input_tokens:,}"
        )

        print(
            f"  Output tokens        : "
            f"{metrics.output_tokens:,}"
        )

        print(
            f"  Total tokens         : "
            f"{metrics.total_tokens:,}"
        )

        print(
            f"  Estimated LLM cost   : "
            f"${metrics.estimated_llm_cost:.6f}"
        )

    # -----------------------------------------------------------------------
    # Scenario-level Accuracy
    # -----------------------------------------------------------------------

    print()
    print("Scenario-level Accuracy")
    print("------------------------")

    print(
        f"{'Scenario':<28}"
        f"{'Rules':>12}"
        f"{'LLM':>12}"
        f"{'Hybrid':>12}"
        f"{'Hybrid Δ':>12}"
    )

    print("-" * 76)

    all_scenarios = sorted(
        set(scenarios.values())
    )

    for scenario in all_scenarios:
        rules_metric = (
            rules_report.by_scenario.get(
                scenario
            )
        )

        llm_metric = (
            llm_report.by_scenario.get(
                scenario
            )
        )

        hybrid_metric = (
            hybrid_report.by_scenario.get(
                scenario
            )
        )

        rules_accuracy = (
            rules_metric.accuracy
            if rules_metric
            else 0.0
        )

        llm_accuracy = (
            llm_metric.accuracy
            if llm_metric
            else 0.0
        )

        hybrid_accuracy = (
            hybrid_metric.accuracy
            if hybrid_metric
            else 0.0
        )

        print(
            f"{scenario:<28}"
            f"{pct(rules_accuracy):>12}"
            f"{pct(llm_accuracy):>12}"
            f"{pct(hybrid_accuracy):>12}"
            f"{delta_pct(hybrid_accuracy, rules_accuracy):>12}"
        )

    # -----------------------------------------------------------------------
    # Scenario-level Automation
    # -----------------------------------------------------------------------

    print()
    print("Scenario-level Automation")
    print("--------------------------")

    print(
        f"{'Scenario':<28}"
        f"{'Rules':>12}"
        f"{'LLM':>12}"
        f"{'Hybrid':>12}"
    )

    print("-" * 64)

    for scenario in all_scenarios:
        rules_metric = (
            rules_report.by_scenario.get(
                scenario
            )
        )

        llm_metric = (
            llm_report.by_scenario.get(
                scenario
            )
        )

        hybrid_metric = (
            hybrid_report.by_scenario.get(
                scenario
            )
        )

        print(
            f"{scenario:<28}"
            f"{pct(rules_metric.automation_rate if rules_metric else 0.0):>12}"
            f"{pct(llm_metric.automation_rate if llm_metric else 0.0):>12}"
            f"{pct(hybrid_metric.automation_rate if hybrid_metric else 0.0):>12}"
        )

    # -----------------------------------------------------------------------
    # Scenario-level automation safety
    # -----------------------------------------------------------------------

    print()
    print("Scenario-level Automation Safety")
    print("---------------------------------")

    print(
        f"{'Scenario':<28}"
        f"{'Rules':>12}"
        f"{'LLM':>12}"
        f"{'Hybrid':>12}"
    )

    print("-" * 64)

    for scenario in all_scenarios:
        rules_metric = (
            rules_report.by_scenario.get(
                scenario
            )
        )

        llm_metric = (
            llm_report.by_scenario.get(
                scenario
            )
        )

        hybrid_metric = (
            hybrid_report.by_scenario.get(
                scenario
            )
        )

        # Display FALSE AUTO-MATCH rate because this is the
        # primary safety signal.
        print(
            f"{scenario:<28}"
            f"{pct(rules_metric.false_auto_match_rate if rules_metric else 0.0):>12}"
            f"{pct(llm_metric.false_auto_match_rate if llm_metric else 0.0):>12}"
            f"{pct(hybrid_metric.false_auto_match_rate if hybrid_metric else 0.0):>12}"
        )

    # -----------------------------------------------------------------------
    # Hybrid vs Rules
    # -----------------------------------------------------------------------

    print()
    print("Hybrid vs Rules")
    print("---------------")

    rules_metrics = (
        rules_report.overall
    )

    hybrid_metrics = (
        hybrid_report.overall
    )

    print(
        f"Accuracy delta              : "
        f"{delta_pct(hybrid_metrics.accuracy, rules_metrics.accuracy)}"
    )

    print(
        f"Precision delta             : "
        f"{delta_pct(hybrid_metrics.precision, rules_metrics.precision)}"
    )

    print(
        f"Recall delta                : "
        f"{delta_pct(hybrid_metrics.recall, rules_metrics.recall)}"
    )

    print(
        f"False-match delta           : "
        f"{delta_pct(hybrid_metrics.false_match_rate, rules_metrics.false_match_rate)}"
    )

    print(
        f"Exception delta             : "
        f"{delta_pct(hybrid_metrics.exception_rate, rules_metrics.exception_rate)}"
    )

    print(
        f"Automation delta            : "
        f"{delta_pct(hybrid_metrics.automation_rate, rules_metrics.automation_rate)}"
    )

    print(
        f"Correct automation delta    : "
        f"{delta_pct(hybrid_metrics.correct_automation_rate, rules_metrics.correct_automation_rate)}"
    )

    print(
        f"Auto-match precision delta  : "
        f"{delta_pct(hybrid_metrics.auto_match_precision, rules_metrics.auto_match_precision)}"
    )

    print(
        f"False auto-match delta      : "
        f"{delta_pct(hybrid_metrics.false_auto_match_rate, rules_metrics.false_auto_match_rate)}"
    )

    print(
        f"LLM invocation delta        : "
        f"{delta_pct(hybrid_metrics.llm_invocation_rate, rules_metrics.llm_invocation_rate)}"
    )

    print()

    # -----------------------------------------------------------------------
    # Benchmark result files
    # -----------------------------------------------------------------------

    print("Benchmark result files")
    print("----------------------")

    print(
        f"Rules  : {RULES_RESULTS_FILE}"
    )

    print(
        f"LLM    : {LLM_RESULTS_FILE}"
    )

    print(
        f"Hybrid : {HYBRID_RESULTS_FILE}"
    )

    print()


if __name__ == "__main__":
    main()

