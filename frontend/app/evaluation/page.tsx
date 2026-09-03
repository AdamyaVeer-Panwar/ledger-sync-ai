"use client";

import Link from "next/link";

type Tone =
  | "copper"
  | "blue"
  | "lime"
  | "amber"
  | "red"
  | "neutral";

type HistoricalComparisonRow = {
  metric: string;
  explanation: string;
  rules: string;
  llm: string;
  hybrid: string;
  tone?: Tone;
};

const historicalComparison: HistoricalComparisonRow[] = [
  {
    metric: "Resolution accuracy",
    explanation:
      "Correct final resolution across the evaluated records.",
    rules: "83.75%",
    llm: "67.50%",
    hybrid: "76.25%",
    tone: "blue",
  },
  {
    metric: "Precision",
    explanation:
      "Correctness of automatically resolved matches.",
    rules: "100%",
    llm: "81.82%",
    hybrid: "100%",
    tone: "lime",
  },
  {
    metric: "Recall",
    explanation:
      "Eligible matches successfully recovered.",
    rules: "80.88%",
    llm: "79.41%",
    hybrid: "89.71%",
    tone: "lime",
  },
  {
    metric: "False-match rate",
    explanation:
      "Incorrect matches accepted as valid.",
    rules: "0%",
    llm: "15%",
    hybrid: "0%",
    tone: "red",
  },
  {
    metric: "Automation rate",
    explanation:
      "Share of records resolved without human review.",
    rules: "68.75%",
    llm: "100%*",
    hybrid: "76.25%",
    tone: "copper",
  },
  {
    metric: "Human review",
    explanation:
      "Records intentionally withheld for manual handling.",
    rules: "8.75%",
    llm: "—",
    hybrid: "23.75%",
    tone: "amber",
  },
  {
    metric: "Failures",
    explanation:
      "Records that failed processing.",
    rules: "—",
    llm: "0%",
    hybrid: "0%",
    tone: "lime",
  },
];

const currentHybrid = [
  {
    value: "76.00%",
    label: "RESOLUTION ACCURACY",
    detail: "400 records evaluated",
    tone: "blue" as Tone,
  },
  {
    value: "100.00%",
    label: "AUTO-MATCH PRECISION",
    detail: "Current Hybrid benchmark",
    tone: "lime" as Tone,
  },
  {
    value: "89.41%",
    label: "AUTO-MATCH RECALL",
    detail: "Current Hybrid benchmark",
    tone: "lime" as Tone,
  },
  {
    value: "0.00%",
    label: "FALSE AUTO-MATCH",
    detail: "Current Hybrid benchmark",
    tone: "copper" as Tone,
  },
];

const currentOperations = [
  {
    value: "90",
    label: "LLM INVOCATIONS",
    detail: "22.50% invocation rate",
    tone: "blue" as Tone,
  },
  {
    value: "78.01 ms",
    label: "P50 LATENCY",
    detail: "Median observed latency",
    tone: "blue" as Tone,
  },
  {
    value: "11.51 s",
    label: "P95 LATENCY",
    detail: "Tail latency",
    tone: "copper" as Tone,
  },
  {
    value: "0",
    label: "FAILURES",
    detail: "400 successful requests",
    tone: "lime" as Tone,
  },
];

const architecturalDimensions = [
  {
    dimension: "Deterministic authority",
    rules: "HIGH",
    llm: "LOW",
    hybrid: "HIGH",
    explanation:
      "Rules remain the source of truth for checks that can be expressed deterministically.",
  },
  {
    dimension: "Semantic coverage",
    rules: "LIMITED",
    llm: "HIGH",
    hybrid: "HIGH",
    explanation:
      "AI extends coverage to cases requiring interpretation rather than exact equality.",
  },
  {
    dimension: "AI dependency",
    rules: "NONE",
    llm: "HIGH",
    hybrid: "BOUNDED",
    explanation:
      "The current Hybrid benchmark invokes the LLM for only 22.50% of records.",
  },
  {
    dimension: "Verification boundary",
    rules: "NATIVE",
    llm: "VARIABLE",
    hybrid: "REQUIRED",
    explanation:
      "A model proposal does not automatically become a financial decision.",
  },
  {
    dimension: "Human escalation",
    rules: "POSSIBLE",
    llm: "VARIABLE",
    hybrid: "EXPLICIT",
    explanation:
      "Ambiguity is represented as a first-class outcome instead of being forced into automation.",
  },
  {
    dimension: "Auditability",
    rules: "HIGH",
    llm: "VARIABLE",
    hybrid: "HIGH",
    explanation:
      "Evidence, confidence, candidates and final policy are separable concepts.",
  },
];

export default function EvaluationPage() {
  return (
    <section className="mx-auto max-w-[1500px]">
      {/* =====================================================
          HEADER
          ===================================================== */}

      <header className="border-b border-[var(--border)] pb-8">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <span className="border border-[var(--blue)] bg-[var(--blue-soft)] px-2 py-1 font-mono text-[8px] font-semibold tracking-[0.16em] text-[var(--blue)]">
                04
              </span>

              <span className="font-mono text-[9px] font-semibold tracking-[0.2em] text-[var(--ink-muted)]">
                ENGINE EVALUATION
              </span>
            </div>

            <h1 className="mt-4 max-w-4xl text-4xl font-semibold leading-[0.95] tracking-[-0.055em] text-[var(--ink)] sm:text-5xl lg:text-6xl">
              Why Hybrid?
            </h1>

            <p className="mt-4 max-w-3xl text-sm leading-7 text-[var(--ink-muted)] sm:text-base">
              Evaluate the reconciliation system as an engineering trade-off:
              correctness, coverage, automation, risk, AI dependency and
              operational behaviour.
            </p>
          </div>

          <div className="border border-[var(--border)] bg-[var(--surface)] px-5 py-4 shadow-[var(--shadow-sm)]">
            <div className="font-mono text-[8px] tracking-[0.17em] text-[var(--ink-muted)]">
              CURRENT BENCHMARK
            </div>

            <div className="mt-2 flex items-end gap-3">
              <span className="font-mono text-3xl font-medium tracking-[-0.04em] text-[var(--ink)]">
                400
              </span>

              <span className="mb-1 font-mono text-[8px] tracking-[0.12em] text-[var(--ink-muted)]">
                RECORDS
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* =====================================================
          CORE ARGUMENT
          ===================================================== */}

      <section className="mt-6 overflow-hidden border border-[var(--navy)] bg-[var(--navy)] text-white shadow-[var(--shadow-md)]">
        <div className="grid lg:grid-cols-[0.7fr_1.3fr]">
          <div className="relative border-b border-[#35485F] p-7 sm:p-9 lg:border-b-0 lg:border-r">
            <div className="absolute left-0 top-0 h-1 w-20 bg-[var(--copper)]" />

            <div className="font-mono text-[8px] tracking-[0.2em] text-[#91A1B1]">
              ENGINEERING THESIS
            </div>

            <h2 className="mt-5 max-w-md text-3xl font-semibold leading-tight tracking-[-0.04em] sm:text-4xl">
              Maximum automation is not maximum correctness.
            </h2>

            <p className="mt-6 max-w-md text-sm leading-6 text-[#AEB9C4]">
              A reconciliation system operates under asymmetric risk. Missing
              a match and accepting the wrong match are not equivalent
              failures.
            </p>

            <div className="mt-8 border-t border-[#35485F] pt-6">
              <div className="font-mono text-[8px] tracking-[0.15em] text-[#718396]">
                DESIGN TARGET
              </div>

              <div className="mt-3 font-mono text-[10px] font-semibold tracking-[0.12em]">
                MORE COVERAGE
                <span className="mx-2 text-[var(--copper)]">
                  +
                </span>
                CONTROLLED RISK
              </div>
            </div>
          </div>

          <div className="p-7 sm:p-9">
            <div className="grid gap-4 md:grid-cols-3">
              <ArchitectureBlock
                title="RULES"
                tone="copper"
                points={[
                  "Deterministic",
                  "Explainable",
                  "No model dependency",
                ]}
              />

              <ArchitectureBlock
                title="LLM"
                tone="blue"
                points={[
                  "Semantic",
                  "Flexible",
                  "Higher inference risk",
                ]}
              />

              <ArchitectureBlock
                title="HYBRID"
                tone="lime"
                points={[
                  "Rules first",
                  "AI bounded",
                  "Verification required",
                ]}
                emphasis
              />
            </div>

            <div className="mt-6 border-t border-[#35485F] pt-6">
              <div className="font-mono text-[8px] tracking-[0.17em] text-[#718396]">
                THE DECISION
              </div>

              <p className="mt-3 max-w-3xl text-sm leading-6 text-[#B6C0CA]">
                Hybrid is not presented as an unconditional winner. It is the
                selected architecture because it creates a controllable
                boundary between deterministic evidence and semantic reasoning.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          CURRENT HYBRID RESULT
          ===================================================== */}

      <section className="mt-8">
        <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--lime)]">
              CURRENT RUN · VERIFIED
            </div>

            <h2 className="mt-2 text-2xl font-semibold tracking-[-0.035em] text-[var(--ink)] sm:text-3xl">
              Latest Hybrid benchmark
            </h2>

            <p className="mt-2 text-xs text-[var(--ink-muted)]">
              Current measured run · 400 records · 0 failures
            </p>
          </div>

          <span className="border border-[var(--lime)] bg-[var(--lime-soft)] px-3 py-2 font-mono text-[8px] font-semibold tracking-[0.12em] text-[var(--lime)]">
            CURRENT EVIDENCE
          </span>
        </div>

        <div className="grid border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow-sm)] sm:grid-cols-2 lg:grid-cols-4">
          {currentHybrid.map((metric, index) => (
            <MetricBlock
              key={metric.label}
              {...metric}
              border={index < currentHybrid.length - 1}
            />
          ))}
        </div>
      </section>

      {/* =====================================================
          THE MOST IMPORTANT VISUAL:
          RISK VS AUTOMATION
          ===================================================== */}

      <section className="mt-8">
        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="overflow-hidden border border-[var(--border)] bg-[var(--surface)]">
            <div className="border-b border-[var(--border)] px-6 py-5">
              <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--ink-soft)]">
                AUTOMATION ↔ RISK
              </div>

              <div className="mt-1 text-xs text-[var(--ink-muted)]">
                Historical comparative experiment
              </div>
            </div>

            <div className="relative p-7 sm:p-9">
              <div className="mb-8 flex items-center justify-between font-mono text-[8px] tracking-[0.12em] text-[var(--ink-muted)]">
                <span>LOW AUTOMATION</span>
                <span>HIGH AUTOMATION</span>
              </div>

              <div className="relative h-[190px]">
                {/* horizontal axis */}

                <div className="absolute left-0 right-0 top-1/2 h-px bg-[var(--border-strong)]" />

                {/* risk axis */}

                <div className="absolute bottom-0 left-1/2 top-0 w-px bg-[var(--border)]" />

                <div className="absolute left-1/2 top-0 -translate-x-1/2 -translate-y-5 font-mono text-[7px] tracking-[0.1em] text-[var(--red)]">
                  HIGHER FALSE-MATCH RISK
                </div>

                {/* Rules */}

                <PositionedPoint
                  label="RULES"
                  value="68.75% / 0%"
                  left="36%"
                  top="54%"
                  tone="copper"
                  detail="automation / false-match"
                />

                {/* Hybrid */}

                <PositionedPoint
                  label="HYBRID"
                  value="76.25% / 0%"
                  left="61%"
                  top="54%"
                  tone="lime"
                  detail="automation / false-match"
                  emphasis
                />

                {/* LLM */}

                <PositionedPoint
                  label="LLM"
                  value="100% / 15%"
                  left="86%"
                  top="25%"
                  tone="red"
                  detail="automation / false-match"
                />
              </div>

              <div className="mt-5 flex items-center justify-between font-mono text-[7px] tracking-[0.1em] text-[var(--ink-muted)]">
                <span>LOW FALSE-MATCH RISK</span>

                <span>HIGHER FALSE-MATCH RISK</span>
              </div>
            </div>
          </div>

          <div className="relative overflow-hidden border border-[var(--copper)] bg-[var(--copper-soft)] p-6 sm:p-8">
            <div className="absolute right-0 top-0 h-full w-1 bg-[var(--copper)]" />

            <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--copper-dark)]">
              THE TRADE-OFF
            </div>

            <h2 className="mt-4 text-2xl font-semibold leading-tight tracking-[-0.035em] text-[var(--ink)] sm:text-3xl">
              100% automation can still be the wrong answer.
            </h2>

            <div className="mt-7 space-y-5">
              <TradeoffLine
                label="LLM-ONLY"
                value="100% automation"
                detail="15% false-match rate"
                tone="red"
              />

              <TradeoffLine
                label="HYBRID"
                value="76.25% automation"
                detail="0% false-match rate"
                tone="lime"
              />

              <TradeoffLine
                label="RULES-ONLY"
                value="68.75% automation"
                detail="0% false-match rate"
                tone="copper"
              />
            </div>

            <p className="mt-7 border-t border-[var(--border)] pt-5 text-sm leading-6 text-[var(--ink-soft)]">
              The engineering problem is therefore not to maximize the first
              number. It is to choose an operating point whose risk is
              acceptable.
            </p>
          </div>
        </div>
      </section>

      {/* =====================================================
          HISTORICAL SCORECARD
          ===================================================== */}

      <section className="mt-8">
        <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--ink-muted)]">
              HISTORICAL COMPARISON
            </div>

            <h2 className="mt-2 text-2xl font-semibold tracking-[-0.035em] text-[var(--ink)] sm:text-3xl">
              Rules-only vs LLM-only vs Hybrid
            </h2>
          </div>

          <span className="font-mono text-[8px] tracking-[0.1em] text-[var(--ink-muted)]">
            OLDER EXPERIMENT · NOT THE CURRENT RUN
          </span>
        </div>

        <div className="overflow-hidden border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow-sm)]">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[920px] border-collapse">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  <th className="w-[36%] bg-[var(--surface-soft)] px-6 py-5 text-left font-mono text-[8px] font-semibold tracking-[0.15em] text-[var(--ink-muted)]">
                    METRIC
                  </th>

                  <th className="w-[21%] bg-[var(--surface-soft)] px-6 py-5 text-left font-mono text-[8px] font-semibold tracking-[0.15em] text-[var(--copper-dark)]">
                    RULES-ONLY
                  </th>

                  <th className="w-[21%] bg-[#E8F1F5] px-6 py-5 text-left font-mono text-[8px] font-semibold tracking-[0.15em] text-[var(--blue)]">
                    LLM-ONLY
                  </th>

                  <th className="relative w-[22%] bg-[var(--lime-soft)] px-6 py-5 text-left font-mono text-[8px] font-semibold tracking-[0.15em] text-[var(--lime)]">
                    <span className="absolute bottom-0 left-0 top-0 w-1 bg-[var(--lime)]" />

                    <span className="ml-1">
                      HYBRID
                    </span>

                    <span className="ml-2 border border-[var(--lime)] bg-white/70 px-1.5 py-1 text-[7px] tracking-[0.08em]">
                      SELECTED
                    </span>
                  </th>
                </tr>
              </thead>

              <tbody>
                {historicalComparison.map(
                  (row) => (
                    <tr
                      key={row.metric}
                      className="border-b border-[var(--border)] last:border-b-0"
                    >
                      <td className="bg-[var(--surface-soft)] px-6 py-5">
                        <div className="font-mono text-[9px] font-semibold tracking-[0.08em] text-[var(--ink)]">
                          {row.metric}
                        </div>

                        <div className="mt-1.5 max-w-sm text-xs leading-5 text-[var(--ink-muted)]">
                          {row.explanation}
                        </div>
                      </td>

                      <td className="px-6 py-5">
                        <ComparisonValue
                          value={row.rules}
                          tone="rules"
                        />
                      </td>

                      <td className="bg-[#F2F7F9] px-6 py-5">
                        <ComparisonValue
                          value={row.llm}
                          tone="llm"
                          danger={
                            row.metric ===
                            "False-match rate"
                          }
                        />
                      </td>

                      <td className="relative bg-[var(--lime-soft)]/70 px-6 py-5">
                        <span className="absolute bottom-0 left-0 top-0 w-1 bg-[var(--lime)]/70" />

                        <ComparisonValue
                          value={row.hybrid}
                          tone="hybrid"
                        />
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>

          <div className="grid border-t border-[var(--border)] bg-[var(--surface-soft)] sm:grid-cols-2">
            <div className="border-b border-[var(--border)] px-6 py-4 sm:border-b-0 sm:border-r">
              <div className="font-mono text-[8px] font-semibold tracking-[0.13em] text-[var(--ink-muted)]">
                IMPORTANT
              </div>

              <div className="mt-1 text-xs leading-5 text-[var(--ink-soft)]">
                Hybrid did not have the highest overall resolution accuracy in
                this historical comparison.
              </div>
            </div>

            <div className="px-6 py-4">
              <div className="font-mono text-[8px] font-semibold tracking-[0.13em] text-[var(--lime)]">
                WHAT MATTERS
              </div>

              <div className="mt-1 text-xs leading-5 text-[var(--ink-soft)]">
                Hybrid combined higher recall with zero measured false-match
                rate while keeping AI usage bounded.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          ARCHITECTURE SCORECARD
          ===================================================== */}

      <section className="mt-8">
        <div className="mb-4">
          <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--ink-muted)]">
            ARCHITECTURE SCORECARD
          </div>

          <h2 className="mt-2 text-2xl font-semibold tracking-[-0.035em] text-[var(--ink)]">
            The numbers explain the outcome. Architecture explains why.
          </h2>
        </div>

        <div className="overflow-hidden border border-[var(--border)] bg-[var(--surface)]">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] border-collapse">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  <th className="w-[34%] bg-[var(--surface-soft)] px-6 py-5 text-left font-mono text-[8px] tracking-[0.14em] text-[var(--ink-muted)]">
                    DIMENSION
                  </th>

                  <th className="bg-[var(--surface-soft)] px-6 py-5 text-left font-mono text-[8px] tracking-[0.14em] text-[var(--copper-dark)]">
                    RULES
                  </th>

                  <th className="bg-[#E8F1F5] px-6 py-5 text-left font-mono text-[8px] tracking-[0.14em] text-[var(--blue)]">
                    LLM
                  </th>

                  <th className="relative bg-[var(--lime-soft)] px-6 py-5 text-left font-mono text-[8px] tracking-[0.14em] text-[var(--lime)]">
                    <span className="absolute bottom-0 left-0 top-0 w-1 bg-[var(--lime)]" />
                    HYBRID
                  </th>
                </tr>
              </thead>

              <tbody>
                {architecturalDimensions.map(
                  (row) => (
                    <tr
                      key={row.dimension}
                      className="border-b border-[var(--border)] last:border-b-0"
                    >
                      <td className="bg-[var(--surface-soft)] px-6 py-5">
                        <div className="font-mono text-[9px] font-semibold tracking-[0.08em] text-[var(--ink)]">
                          {row.dimension}
                        </div>

                        <p className="mt-1.5 max-w-sm text-xs leading-5 text-[var(--ink-muted)]">
                          {row.explanation}
                        </p>
                      </td>

                      <td className="px-6 py-5">
                        <ArchitectureValue value={row.rules} />
                      </td>

                      <td className="bg-[#F2F7F9] px-6 py-5">
                        <ArchitectureValue value={row.llm} />
                      </td>

                      <td className="relative bg-[var(--lime-soft)]/65 px-6 py-5">
                        <span className="absolute bottom-0 left-0 top-0 w-1 bg-[var(--lime)]/60" />

                        <ArchitectureValue
                          value={row.hybrid}
                          highlight
                        />
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* =====================================================
          CURRENT OPERATIONAL PROFILE
          ===================================================== */}

      <section className="mt-8">
        <div className="mb-4">
          <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--ink-muted)]">
            CURRENT OPERATIONAL PROFILE
          </div>

          <h2 className="mt-2 text-2xl font-semibold tracking-[-0.035em] text-[var(--ink)]">
            AI is a selective dependency.
          </h2>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-[var(--ink-muted)]">
            The latest benchmark invoked the LLM on only 22.50% of records.
            The remaining work stays on the deterministic path.
          </p>
        </div>

        <div className="grid border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow-sm)] sm:grid-cols-2 lg:grid-cols-4">
          {currentOperations.map(
            (metric, index) => (
              <MetricBlock
                key={metric.label}
                {...metric}
                border={
                  index <
                  currentOperations.length - 1
                }
              />
            ),
          )}
        </div>
      </section>

      {/* =====================================================
          LATENCY
          ===================================================== */}

      <section className="mt-8 grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
        <div className="border border-[var(--border)] bg-[var(--surface)] p-6 sm:p-8">
          <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--ink-muted)]">
            LATENCY DISTRIBUTION
          </div>

          <div className="mt-8 space-y-7">
            <LatencyBar
              label="P50"
              value="78.01 ms"
              width="18%"
              tone="blue"
            />

            <LatencyBar
              label="P95"
              value="11.51 s"
              width="95%"
              tone="copper"
            />
          </div>

          <div className="mt-8 border-t border-[var(--border)] pt-5">
            <div className="font-mono text-[8px] tracking-[0.13em] text-[var(--ink-muted)]">
              TOTAL BENCHMARK
            </div>

            <div className="mt-2 font-mono text-xl font-semibold text-[var(--ink)]">
              804.35 s
            </div>

            <div className="mt-1 text-xs text-[var(--ink-muted)]">
              400 records · 0 failures
            </div>
          </div>
        </div>

        <div className="border border-[var(--border)] bg-[var(--surface-soft)] p-6 sm:p-8">
          <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--ink-muted)]">
            ENGINEERING INTERPRETATION
          </div>

          <h2 className="mt-4 max-w-2xl text-2xl font-semibold leading-tight tracking-[-0.035em] text-[var(--ink)]">
            The median is fast. The tail deserves attention.
          </h2>

          <p className="mt-4 max-w-2xl text-sm leading-6 text-[var(--ink-muted)]">
            The current benchmark shows a large gap between P50 and P95.
            That means the expensive path has a material effect on tail
            latency even though the median record is substantially faster.
          </p>

          <div className="mt-7 border-l-2 border-[var(--copper)] pl-4 text-sm leading-6 text-[var(--ink-soft)]">
            Recommended next engineering target: profile the slower AI and
            retrieval path instead of optimizing the median in isolation.
          </div>
        </div>
      </section>

      {/* =====================================================
          DATA INTEGRITY
          ===================================================== */}

      <section className="mt-8 border border-[var(--border)] bg-[var(--surface)] p-6 sm:p-8">
        <div className="grid gap-6 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--ink-muted)]">
              EVALUATION INTEGRITY
            </div>

            <h2 className="mt-3 text-xl font-semibold tracking-[-0.03em] text-[var(--ink)]">
              Current measurements and historical comparisons are intentionally
              separated.
            </h2>

            <p className="mt-3 max-w-3xl text-sm leading-6 text-[var(--ink-muted)]">
              The current Hybrid metrics are from the latest 400-record
              benchmark. The Rules-only / LLM-only / Hybrid scorecard is an
              older comparison experiment. The page does not present those
              datasets as one synchronized experiment.
            </p>
          </div>

          <div className="border border-[var(--copper)] bg-[var(--copper-soft)] px-5 py-4">
            <div className="font-mono text-[8px] font-semibold tracking-[0.14em] text-[var(--copper-dark)]">
              NO DATA BLENDING
            </div>

            <div className="mt-2 text-xs text-[var(--ink-soft)]">
              Measurements remain tied to their experiment.
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          FINAL DECISION
          ===================================================== */}

      <section className="mt-8 overflow-hidden border border-[var(--copper)] bg-[var(--copper-soft)]">
        <div className="flex flex-col gap-7 p-7 sm:p-9 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--copper-dark)]">
              ENGINEERING DECISION
            </div>

            <h2 className="mt-3 max-w-4xl text-3xl font-semibold leading-tight tracking-[-0.04em] text-[var(--ink)]">
              Keep deterministic authority. Use AI to expand coverage. Verify
              before authorization.
            </h2>

            <p className="mt-4 max-w-4xl text-sm leading-6 text-[var(--ink-soft)]">
              The current evidence does not say that Hybrid wins every metric.
              It shows why bounded AI is a useful architectural direction:
              semantic reasoning can be introduced without making the model the
              final authority.
            </p>
          </div>

          <Link
            href="/engineering"
            className="group inline-flex shrink-0 items-center justify-center gap-3 border border-[var(--navy)] bg-white px-6 py-4 font-mono text-[9px] font-semibold tracking-[0.14em] text-[var(--navy)] shadow-[var(--shadow-sm)] transition-all hover:-translate-y-px hover:border-[var(--copper-dark)] hover:bg-[var(--copper-soft)] hover:text-[var(--copper-dark)]"
          >
            OPEN ENGINEERING REPORT
            <span className="transition-transform group-hover:translate-x-1">
              →
            </span>
          </Link>
        </div>
      </section>

      <footer className="flex flex-col gap-2 border-t border-[var(--border)] py-7 font-mono text-[8px] tracking-[0.08em] text-[var(--ink-muted)] sm:flex-row sm:justify-between">
        <span>
          CURRENT HYBRID · 400 RECORDS · 0 FAILURES
        </span>

        <span>
          HISTORICAL COMPARISON SHOWN SEPARATELY
        </span>
      </footer>
    </section>
  );
}

/* =============================================================
   ARCHITECTURE BLOCK
   ============================================================= */

function ArchitectureBlock({
  title,
  tone,
  points,
  emphasis = false,
}: {
  title: string;
  tone: Tone;
  points: string[];
  emphasis?: boolean;
}) {
  const accent =
    tone === "copper"
      ? "text-[var(--copper)]"
      : tone === "blue"
        ? "text-[#73B9D2]"
        : "text-[var(--lime)]";

  return (
    <div
      className={[
        "relative min-h-[190px] p-5",
        emphasis
          ? "bg-[#1D3047]"
          : "bg-[var(--navy)]",
      ].join(" ")}
    >
      {emphasis && (
        <div className="absolute left-0 top-0 h-full w-1 bg-[var(--lime)]" />
      )}

      <div className="font-mono text-[10px] font-semibold tracking-[0.15em] text-white">
        {title}
      </div>

      <div
        className={`mt-1 font-mono text-[8px] tracking-[0.13em] ${accent}`}
      >
        {emphasis ? "SELECTED ARCHITECTURE" : "APPROACH"}
      </div>

      <div className="mt-7 space-y-3">
        {points.map((point) => (
          <div
            key={point}
            className="flex items-center gap-2"
          >
            <span className={accent}>
              •
            </span>

            <span className="font-mono text-[8px] text-[#9DABB9]">
              {point}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* =============================================================
   METRIC BLOCK
   ============================================================= */

function MetricBlock({
  value,
  label,
  detail,
  tone,
  border = true,
}: {
  value: string;
  label: string;
  detail: string;
  tone: Tone;
  border?: boolean;
}) {
  const accent =
    tone === "lime"
      ? "bg-[var(--lime)]"
      : tone === "blue"
        ? "bg-[var(--blue)]"
        : tone === "copper"
          ? "bg-[var(--copper)]"
          : tone === "red"
            ? "bg-[var(--red)]"
            : "bg-[var(--amber)]";

  return (
    <div
      className={[
        "p-6",
        border
          ? "border-b border-[var(--border)] lg:border-b-0 lg:border-r"
          : "",
      ].join(" ")}
    >
      <div className={`mb-4 h-1 w-8 ${accent}`} />

      <div className="font-mono text-2xl font-medium tracking-[-0.035em] text-[var(--ink)]">
        {value}
      </div>

      <div className="mt-2 font-mono text-[8px] font-semibold tracking-[0.14em] text-[var(--ink-soft)]">
        {label}
      </div>

      <div className="mt-1.5 text-xs text-[var(--ink-muted)]">
        {detail}
      </div>
    </div>
  );
}

/* =============================================================
   POSITIONED POINT
   ============================================================= */

function PositionedPoint({
  label,
  value,
  left,
  top,
  tone,
  detail,
  emphasis = false,
}: {
  label: string;
  value: string;
  left: string;
  top: string;
  tone: Tone;
  detail: string;
  emphasis?: boolean;
}) {
  const point =
    tone === "lime"
      ? "bg-[var(--lime)]"
      : tone === "copper"
        ? "bg-[var(--copper)]"
        : "bg-[var(--red)]";

  const text =
    tone === "lime"
      ? "text-[var(--lime)]"
      : tone === "copper"
        ? "text-[var(--copper-dark)]"
        : "text-[var(--red)]";

  return (
    <div
      className="absolute"
      style={{
        left,
        top,
        transform: "translate(-50%, -50%)",
      }}
    >
      <div className="flex items-center gap-2">
        <span
          className={[
            "h-3 w-3 rounded-full ring-4 ring-[var(--surface)]",
            point,
            emphasis
              ? "scale-125"
              : "",
          ].join(" ")}
        />

        <div className="border border-[var(--border)] bg-[var(--surface)] px-3 py-2 shadow-[var(--shadow-sm)]">
          <div
            className={`font-mono text-[8px] font-semibold tracking-[0.13em] ${text}`}
          >
            {label}
          </div>

          <div className="mt-1 font-mono text-[9px] font-semibold text-[var(--ink)]">
            {value}
          </div>

          <div className="mt-1 text-[8px] text-[var(--ink-muted)]">
            {detail}
          </div>
        </div>
      </div>
    </div>
  );
}

/* =============================================================
   TRADE-OFF LINE
   ============================================================= */

function TradeoffLine({
  label,
  value,
  detail,
  tone,
}: {
  label: string;
  value: string;
  detail: string;
  tone: Tone;
}) {
  const accent =
    tone === "red"
      ? "bg-[var(--red)]"
      : tone === "lime"
        ? "bg-[var(--lime)]"
        : "bg-[var(--copper)]";

  const text =
    tone === "red"
      ? "text-[var(--red)]"
      : tone === "lime"
        ? "text-[var(--lime)]"
        : "text-[var(--copper-dark)]";

  return (
    <div className="flex items-center gap-4">
      <span
        className={`h-8 w-1 shrink-0 ${accent}`}
      />

      <div>
        <div className={`font-mono text-[8px] font-semibold tracking-[0.13em] ${text}`}>
          {label}
        </div>

        <div className="mt-1 font-mono text-sm font-semibold text-[var(--ink)]">
          {value}
        </div>

        <div className="mt-1 text-xs text-[var(--ink-muted)]">
          {detail}
        </div>
      </div>
    </div>
  );
}

/* =============================================================
   COMPARISON VALUE
   ============================================================= */

function ComparisonValue({
  value,
  tone,
  danger = false,
}: {
  value: string;
  tone: "rules" | "llm" | "hybrid";
  danger?: boolean;
}) {
  const className = danger
    ? "text-[var(--red)]"
    : tone === "hybrid"
      ? "text-[var(--lime)]"
      : tone === "llm"
        ? "text-[var(--blue)]"
        : "text-[var(--copper-dark)]";

  return (
    <span
      className={`font-mono text-sm font-semibold tracking-[-0.02em] ${className}`}
    >
      {value}
    </span>
  );
}

/* =============================================================
   ARCHITECTURE VALUE
   ============================================================= */

function ArchitectureValue({
  value,
  highlight = false,
}: {
  value: string;
  highlight?: boolean;
}) {
  return (
    <span
      className={[
        "font-mono text-[8px] font-semibold tracking-[0.11em]",
        highlight
          ? "text-[var(--lime)]"
          : value === "LOW" ||
              value === "LIMITED" ||
              value === "VARIABLE"
            ? "text-[var(--ink-muted)]"
            : "text-[var(--ink-soft)]",
      ].join(" ")}
    >
      {value}
    </span>
  );
}

/* =============================================================
   LATENCY BAR
   ============================================================= */

function LatencyBar({
  label,
  value,
  width,
  tone,
}: {
  label: string;
  value: string;
  width: string;
  tone: "blue" | "copper";
}) {
  const bar =
    tone === "blue"
      ? "bg-[var(--blue)]"
      : "bg-[var(--copper)]";

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <span className="font-mono text-[8px] font-semibold tracking-[0.14em] text-[var(--ink-soft)]">
          {label}
        </span>

        <span className="font-mono text-sm font-semibold text-[var(--ink)]">
          {value}
        </span>
      </div>

      <div className="h-3 bg-[var(--surface-muted)]">
        <div
          className={`h-full ${bar}`}
          style={{ width }}
        />
      </div>
    </div>
  );
}