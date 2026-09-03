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
    detail: "No incorrect automatic matches",
    tone: "lime" as Tone,
  },
  {
    value: "89.41%",
    label: "AUTO-MATCH RECALL",
    detail: "Eligible matches recovered",
    tone: "lime" as Tone,
  },
  {
    value: "0.00%",
    label: "FALSE AUTO-MATCH",
    detail: "Measured in current benchmark",
    tone: "copper" as Tone,
  },
];

const currentOperations = [
  {
    value: "90",
    label: "LLM INVOCATIONS",
    detail: "22.50% of records",
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
      "Evidence, confidence, candidates and final policy remain separable concepts.",
  },
];

const scenarioHighlights = [
  {
    scenario: "PARTIAL REFUND",
    rules: "0%",
    llm: "100%",
    hybrid: "96.67%",
    message:
      "Hybrid substantially improves over the deterministic baseline while avoiding unconditional LLM control.",
    tone: "lime" as Tone,
  },
  {
    scenario: "MULTIPLE CANDIDATES",
    rules: "100%",
    llm: "0%",
    hybrid: "100%",
    message:
      "The deterministic pipeline retains full accuracy on this scenario.",
    tone: "blue" as Tone,
  },
  {
    scenario: "MISSING LEDGER",
    rules: "100%",
    llm: "0%",
    hybrid: "0%",
    message:
      "The current system still has a known coverage gap that should not be hidden.",
    tone: "amber" as Tone,
  },
  {
    scenario: "WRONG MERCHANT",
    rules: "100%",
    llm: "0%",
    hybrid: "0%",
    message:
      "Merchant consistency remains a deterministic safety boundary.",
    tone: "copper" as Tone,
  },
];

function toneText(tone: Tone): string {
  switch (tone) {
    case "copper":
      return "text-[#A85F3E]";
    case "blue":
      return "text-[#557889]";
    case "lime":
      return "text-[#617454]";
    case "amber":
      return "text-[#A97832]";
    case "red":
      return "text-[#A44A3D]";
    default:
      return "text-[#59636A]";
  }
}

function toneFill(tone: Tone): string {
  switch (tone) {
    case "copper":
      return "bg-[#B56A45]";
    case "blue":
      return "bg-[#557889]";
    case "lime":
      return "bg-[#617454]";
    case "amber":
      return "bg-[#A97832]";
    case "red":
      return "bg-[#A44A3D]";
    default:
      return "bg-[#59636A]";
  }
}

export default function EvaluationPage() {
  return (
    <main className="mx-auto max-w-[1500px] text-[var(--ink)]">
      {/* =====================================================
          PAGE NAV
          ===================================================== */}

      <div className="sticky top-0 z-30 -mx-4 border-b border-[var(--border)] bg-[var(--background)]/95 px-4 py-3 backdrop-blur sm:-mx-6 sm:px-6">
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/"
            className="font-mono text-[9px] font-semibold tracking-[0.18em] text-[var(--ink-muted)] transition-colors hover:text-[var(--copper-dark)]"
          >
            LEDGERSYNC / EVALUATION
          </Link>

          <nav className="hidden items-center gap-6 md:flex">
            {[
              ["benchmark", "BENCHMARK"],
              ["scorecard", "SCORECARD"],
              ["scenarios", "SCENARIOS"],
              ["architecture", "ARCHITECTURE"],
              ["operations", "OPERATIONS"],
              ["integrity", "INTEGRITY"],
            ].map(([href, label]) => (
              <a
                key={href}
                href={`#${href}`}
                className="font-mono text-[8px] tracking-[0.12em] text-[var(--ink-muted)] transition-colors hover:text-[var(--ink)]"
              >
                {label}
              </a>
            ))}
          </nav>

          <span className="font-mono text-[8px] font-semibold tracking-[0.12em] text-[var(--lime)]">
            ● EVIDENCE
          </span>
        </div>
      </div>

      {/* =====================================================
          HERO
          ===================================================== */}

      <header className="border-b border-[var(--border)] py-14 sm:py-18 lg:py-22">
        <div className="grid gap-12 lg:grid-cols-[1fr_390px] lg:items-end">
          <div>
            <div className="flex items-center gap-3">
              <span className="font-mono text-[9px] font-semibold tracking-[0.2em] text-[var(--blue)]">
                04
              </span>

              <span className="h-px w-9 bg-[var(--copper)]" />

              <span className="font-mono text-[10px] font-semibold tracking-[0.2em] text-[var(--ink-muted)]">
                ENGINE EVALUATION
              </span>
            </div>

            <h1 className="mt-7 max-w-6xl text-[clamp(3.6rem,8vw,7.4rem)] font-semibold leading-[0.86] tracking-[-0.075em]">
              Why
              <br />
              Hybrid?
            </h1>

            <p className="mt-8 max-w-3xl text-lg leading-8 text-[var(--ink-soft)] sm:text-xl">
              More coverage without giving the model financial authority.
              Evaluation here is about the operating point—not about
              maximizing automation for its own sake.
            </p>
          </div>

          <div className="border-l border-[var(--border)] pl-8">
            <div className="font-mono text-[10px] font-semibold tracking-[0.16em] text-[var(--ink-muted)]">
              CURRENT BENCHMARK
            </div>

            <div className="mt-3 font-mono text-6xl font-semibold tracking-[-0.06em]">
              400
            </div>

            <div className="mt-1 font-mono text-[9px] tracking-[0.13em] text-[var(--ink-muted)]">
              RECORDS EVALUATED
            </div>

            <div className="mt-7 flex items-center gap-2 font-mono text-[9px] font-semibold tracking-[0.12em] text-[var(--lime)]">
              <span className="h-2.5 w-2.5 rounded-full bg-[var(--lime)]" />
              400 / 400 SUCCESSFUL REQUESTS
            </div>
          </div>
        </div>
      </header>

      {/* =====================================================
          CORE ARGUMENT
          ===================================================== */}

      <section className="border-b border-[var(--border)] py-14 lg:py-16">
        <div className="grid gap-12 lg:grid-cols-[0.72fr_1.28fr] lg:items-center">
          <div>
            <div className="font-mono text-[10px] font-semibold tracking-[0.19em] text-[var(--copper-dark)]">
              THE ENGINEERING QUESTION
            </div>

            <h2 className="mt-5 max-w-xl text-3xl font-semibold leading-[1.05] tracking-[-0.045em] sm:text-4xl lg:text-5xl">
              How much reasoning should the system outsource?
            </h2>
          </div>

          <div className="border-l-2 border-[var(--copper)] pl-7">
            <p className="max-w-3xl text-lg leading-8 text-[var(--ink-soft)]">
              Reconciliation has asymmetric risk. Failing to discover a
              legitimate match is undesirable, but automatically accepting an
              incorrect financial match is a different class of failure.
            </p>

            <div className="mt-7 grid gap-7 sm:grid-cols-2">
              <Argument
                label="RULES-ONLY"
                value="CONTROL"
                detail="Strong deterministic authority, narrower semantic coverage."
                tone="copper"
              />

              <Argument
                label="LLM-ONLY"
                value="COVERAGE"
                detail="Broad semantic reasoning, but materially higher automated risk."
                tone="blue"
              />

              <Argument
                label="HYBRID"
                value="BALANCE"
                detail="Rules first, AI selective, verification before policy."
                tone="lime"
              />

              <Argument
                label="TARGET"
                value="SAFE AUTOMATION"
                detail="Increase useful automation without weakening financial controls."
                tone="amber"
              />
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          CURRENT BENCHMARK
          ===================================================== */}

      <section
        id="benchmark"
        className="scroll-mt-20 py-14 lg:py-16"
      >
        <div className="flex flex-col gap-4 border-b border-[var(--border)] pb-7 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="font-mono text-[10px] font-semibold tracking-[0.19em] text-[var(--lime)]">
              01 / CURRENT EVIDENCE
            </div>

            <h2 className="mt-3 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
              Latest Hybrid benchmark
            </h2>

            <p className="mt-3 max-w-3xl text-base leading-7 text-[var(--ink-muted)]">
              Current measured run. This is the benchmark that should be
              treated as the primary evidence surface.
            </p>
          </div>

          <div className="font-mono text-[9px] tracking-[0.1em] text-[var(--ink-muted)]">
            HYBRID / CURRENT / 400 RECORDS
          </div>
        </div>

        <div className="grid gap-10 pt-9 sm:grid-cols-2 lg:grid-cols-4">
          {currentHybrid.map((metric) => (
            <CurrentMetric
              key={metric.label}
              {...metric}
            />
          ))}
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-[1fr_0.62fr]">
          <div className="border-y border-[var(--border)] py-7">
            <div className="font-mono text-[9px] font-semibold tracking-[0.15em] text-[var(--ink-muted)]">
              READING THE CURRENT RUN
            </div>

            <div className="mt-5 grid gap-8 sm:grid-cols-3">
              <Interpretation
                number="01"
                title="76.00%"
                detail="overall resolution accuracy"
                tone="blue"
              />

              <Interpretation
                number="02"
                title="100.00%"
                detail="auto-match precision"
                tone="lime"
              />

              <Interpretation
                number="03"
                title="0.00%"
                detail="false auto-match rate"
                tone="copper"
              />
            </div>
          </div>

          <div className="border-l-2 border-[var(--lime)] pl-6 py-1">
            <div className="font-mono text-[9px] font-semibold tracking-[0.15em] text-[var(--lime)]">
              PRIMARY SAFETY SIGNAL
            </div>

            <div className="mt-3 text-2xl font-semibold tracking-[-0.03em]">
              0% measured false auto-match
            </div>

            <p className="mt-3 text-sm leading-6 text-[var(--ink-muted)]">
              This is the relevant metric when evaluating whether automatic
              financial matches were incorrectly authorized.
            </p>
          </div>
        </div>
      </section>

      {/* =====================================================
          HISTORICAL SCORECARD
          ===================================================== */}

      <section
        id="scorecard"
        className="scroll-mt-20 border-y border-[var(--border)] py-14 lg:py-16"
      >
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="font-mono text-[10px] font-semibold tracking-[0.19em] text-[var(--ink-muted)]">
              02 / HISTORICAL COMPARISON
            </div>

            <h2 className="mt-3 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
              Three operating models.
            </h2>

            <p className="mt-3 max-w-3xl text-base leading-7 text-[var(--ink-muted)]">
              An older controlled experiment comparing deterministic rules,
              unconstrained LLM reasoning and the Hybrid architecture.
            </p>
          </div>

          <span className="font-mono text-[9px] tracking-[0.1em] text-[var(--amber)]">
            HISTORICAL · NOT CURRENT
          </span>
        </div>

        <div className="mt-9 overflow-x-auto">
          <table className="w-full min-w-[980px] border-collapse">
            <thead>
              <tr className="border-b-2 border-[var(--navy)]">
                <th className="w-[36%] bg-[var(--surface-soft)] px-6 py-5 text-left font-mono text-[10px] font-semibold tracking-[0.14em] text-[var(--ink-muted)]">
                  METRIC
                </th>

                <th className="w-[21%] bg-[var(--surface-soft)] px-6 py-5 text-left font-mono text-[10px] font-semibold tracking-[0.14em] text-[var(--copper-dark)]">
                  RULES-ONLY
                </th>

                <th className="w-[21%] bg-[#EAF2F5] px-6 py-5 text-left font-mono text-[10px] font-semibold tracking-[0.14em] text-[var(--blue)]">
                  LLM-ONLY
                </th>

                <th className="relative w-[22%] bg-[var(--lime-soft)] px-6 py-5 text-left font-mono text-[10px] font-semibold tracking-[0.14em] text-[var(--lime)]">
                  <span className="absolute bottom-0 left-0 top-0 w-1 bg-[var(--lime)]" />
                  HYBRID
                  <span className="ml-2 border border-[var(--lime)] bg-white/75 px-1.5 py-1 text-[8px]">
                    SELECTED
                  </span>
                </th>
              </tr>
            </thead>

            <tbody>
              {historicalComparison.map((row) => (
                <tr
                  key={row.metric}
                  className="border-b border-[var(--border)] transition-colors hover:bg-[var(--surface-soft)]"
                >
                  <td className="bg-[var(--surface-soft)] px-6 py-6">
                    <div className="font-mono text-[10px] font-semibold tracking-[0.06em]">
                      {row.metric}
                    </div>

                    <div className="mt-2 max-w-md text-sm leading-6 text-[var(--ink-muted)]">
                      {row.explanation}
                    </div>
                  </td>

                  <td className="px-6 py-6">
                    <ScoreValue
                      value={row.rules}
                      tone="rules"
                    />
                  </td>

                  <td className="bg-[#F3F8FA] px-6 py-6">
                    <ScoreValue
                      value={row.llm}
                      tone="llm"
                      danger={
                        row.metric ===
                        "False-match rate"
                      }
                    />
                  </td>

                  <td className="relative bg-[var(--lime-soft)]/70 px-6 py-6">
                    <span className="absolute bottom-0 left-0 top-0 w-1 bg-[var(--lime)]/60" />

                    <ScoreValue
                      value={row.hybrid}
                      tone="hybrid"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-7 grid gap-6 lg:grid-cols-2">
          <Callout
            label="IMPORTANT"
            text="Hybrid did not have the highest overall resolution accuracy in this historical experiment."
            tone="amber"
          />

          <Callout
            label="WHY HYBRID REMAINS INTERESTING"
            text="It combines higher recall with zero measured false-match rate while keeping AI bounded."
            tone="lime"
          />
        </div>
      </section>

      {/* =====================================================
          SCENARIO ANALYSIS
          ===================================================== */}

      <section
        id="scenarios"
        className="scroll-mt-20 py-14 lg:py-16"
      >
        <div>
          <div className="font-mono text-[10px] font-semibold tracking-[0.19em] text-[var(--ink-muted)]">
            03 / SCENARIO ANALYSIS
          </div>

          <h2 className="mt-3 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
            Where the architectures actually differ.
          </h2>

          <p className="mt-3 max-w-3xl text-base leading-7 text-[var(--ink-muted)]">
            The aggregate score hides the most useful engineering information:
            which classes of financial ambiguity each architecture can and
            cannot handle.
          </p>
        </div>

        <div className="mt-9 grid gap-px border-y border-[var(--border)] bg-[var(--border)] lg:grid-cols-2">
          {scenarioHighlights.map((item) => (
            <div
              key={item.scenario}
              className="bg-[var(--background)] p-7 sm:p-8"
            >
              <div className="flex items-center justify-between gap-5">
                <span className="font-mono text-[10px] font-semibold tracking-[0.14em]">
                  {item.scenario}
                </span>

                <span
                  className={`font-mono text-[9px] font-semibold tracking-[0.12em] ${toneText(item.tone)}`}
                >
                  HYBRID {item.hybrid}
                </span>
              </div>

              <div className="mt-7 grid grid-cols-3 gap-5">
                <ScenarioValue
                  label="RULES"
                  value={item.rules}
                  tone="copper"
                />

                <ScenarioValue
                  label="LLM"
                  value={item.llm}
                  tone="blue"
                />

                <ScenarioValue
                  label="HYBRID"
                  value={item.hybrid}
                  tone="lime"
                />
              </div>

              <p className="mt-7 border-t border-[var(--border)] pt-5 text-sm leading-6 text-[var(--ink-muted)]">
                {item.message}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* =====================================================
          ARCHITECTURAL SCORECARD
          ===================================================== */}

      <section
        id="architecture"
        className="scroll-mt-20 border-y border-[var(--border)] py-14 lg:py-16"
      >
        <div>
          <div className="font-mono text-[10px] font-semibold tracking-[0.19em] text-[var(--ink-muted)]">
            04 / ARCHITECTURE
          </div>

          <h2 className="mt-3 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
            The numbers explain the outcome. Architecture explains why.
          </h2>
        </div>

        <div className="mt-9 overflow-x-auto">
          <table className="w-full min-w-[960px] border-collapse">
            <thead>
              <tr className="border-b-2 border-[var(--navy)]">
                <th className="w-[34%] bg-[var(--surface-soft)] px-6 py-5 text-left font-mono text-[10px] tracking-[0.14em] text-[var(--ink-muted)]">
                  DIMENSION
                </th>

                <th className="bg-[var(--surface-soft)] px-6 py-5 text-left font-mono text-[10px] tracking-[0.14em] text-[var(--copper-dark)]">
                  RULES
                </th>

                <th className="bg-[#EAF2F5] px-6 py-5 text-left font-mono text-[10px] tracking-[0.14em] text-[var(--blue)]">
                  LLM
                </th>

                <th className="relative bg-[var(--lime-soft)] px-6 py-5 text-left font-mono text-[10px] tracking-[0.14em] text-[var(--lime)]">
                  <span className="absolute bottom-0 left-0 top-0 w-1 bg-[var(--lime)]" />
                  HYBRID
                </th>
              </tr>
            </thead>

            <tbody>
              {architecturalDimensions.map((row) => (
                <tr
                  key={row.dimension}
                  className="border-b border-[var(--border)] transition-colors hover:bg-[var(--surface-soft)]"
                >
                  <td className="bg-[var(--surface-soft)] px-6 py-6">
                    <div className="font-mono text-[10px] font-semibold tracking-[0.06em]">
                      {row.dimension}
                    </div>

                    <p className="mt-2 max-w-sm text-sm leading-6 text-[var(--ink-muted)]">
                      {row.explanation}
                    </p>
                  </td>

                  <td className="px-6 py-6">
                    <ArchitectureValue value={row.rules} />
                  </td>

                  <td className="bg-[#F3F8FA] px-6 py-6">
                    <ArchitectureValue value={row.llm} />
                  </td>

                  <td className="relative bg-[var(--lime-soft)]/70 px-6 py-6">
                    <span className="absolute bottom-0 left-0 top-0 w-1 bg-[var(--lime)]/60" />

                    <ArchitectureValue
                      value={row.hybrid}
                      highlight
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* =====================================================
          OPERATIONS
          ===================================================== */}

      <section
        id="operations"
        className="scroll-mt-20 py-14 lg:py-16"
      >
        <div>
          <div className="font-mono text-[10px] font-semibold tracking-[0.19em] text-[var(--ink-muted)]">
            05 / OPERATIONS
          </div>

          <h2 className="mt-3 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
            AI is a selective dependency.
          </h2>

          <p className="mt-3 max-w-3xl text-base leading-7 text-[var(--ink-muted)]">
            The latest Hybrid benchmark invoked the model on 22.50% of records.
            The deterministic path remains the default.
          </p>
        </div>

        <div className="mt-9 grid gap-10 border-y border-[var(--border)] py-9 sm:grid-cols-2 lg:grid-cols-4">
          {currentOperations.map((metric) => (
            <CurrentMetric
              key={metric.label}
              {...metric}
            />
          ))}
        </div>

        <div className="mt-11 grid gap-10 lg:grid-cols-[0.8fr_1.2fr]">
          <div>
            <div className="font-mono text-[9px] font-semibold tracking-[0.15em] text-[var(--ink-muted)]">
              LATENCY DISTRIBUTION
            </div>

            <div className="mt-7 space-y-7">
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

            <div className="mt-8 border-t border-[var(--border)] pt-6">
              <div className="font-mono text-[9px] tracking-[0.13em] text-[var(--ink-muted)]">
                TOTAL BENCHMARK
              </div>

              <div className="mt-2 font-mono text-2xl font-semibold">
                804.35 s
              </div>

              <div className="mt-1 text-sm text-[var(--ink-muted)]">
                400 records · 0 failures
              </div>
            </div>
          </div>

          <div className="border-l-2 border-[var(--blue)] pl-7">
            <div className="font-mono text-[9px] font-semibold tracking-[0.15em] text-[var(--blue)]">
              ENGINEERING INTERPRETATION
            </div>

            <h3 className="mt-4 max-w-2xl text-2xl font-semibold leading-tight tracking-[-0.035em]">
              The median is fast. The tail deserves attention.
            </h3>

            <p className="mt-4 max-w-2xl text-base leading-7 text-[var(--ink-soft)]">
              The large P50/P95 gap indicates that the expensive path has a
              material effect on tail latency even though most records complete
              substantially faster.
            </p>

            <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--ink-muted)]">
              The next optimization target should therefore be the slower AI
              and retrieval path, not median latency in isolation.
            </p>
          </div>
        </div>
      </section>

      {/* =====================================================
          INTEGRITY
          ===================================================== */}

      <section
        id="integrity"
        className="scroll-mt-20 border-y border-[var(--border)] py-14 lg:py-16"
      >
        <div className="grid gap-10 lg:grid-cols-[1fr_330px] lg:items-center">
          <div>
            <div className="font-mono text-[10px] font-semibold tracking-[0.19em] text-[var(--ink-muted)]">
              06 / EVALUATION INTEGRITY
            </div>

            <h2 className="mt-4 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
              Current evidence stays separate from historical evidence.
            </h2>

            <p className="mt-4 max-w-3xl text-base leading-7 text-[var(--ink-muted)]">
              The current Hybrid metrics come from the latest 400-record
              benchmark. The Rules-only / LLM-only / Hybrid scorecard represents
              an older experiment. They are intentionally not presented as one
              synchronized run.
            </p>
          </div>

          <div className="border-l-2 border-[var(--copper)] bg-[var(--copper-soft)] px-6 py-5">
            <div className="font-mono text-[10px] font-semibold tracking-[0.14em] text-[var(--copper-dark)]">
              NO DATA BLENDING
            </div>

            <div className="mt-2 text-base leading-6 text-[var(--ink-soft)]">
              Measurements remain attached to the experiment that produced
              them.
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          ENGINEERING DECISION
          ===================================================== */}

      <section className="py-16 lg:py-20">
        <div className="border-t-2 border-[var(--navy)] pt-10">
          <div className="grid gap-12 lg:grid-cols-[1fr_390px] lg:items-center">
            <div>
              <div className="font-mono text-[10px] font-semibold tracking-[0.19em] text-[var(--copper-dark)]">
                ENGINEERING DECISION
              </div>

              <h2 className="mt-5 max-w-5xl text-4xl font-semibold leading-[0.94] tracking-[-0.055em] sm:text-5xl lg:text-6xl">
                Keep deterministic authority.
                <br />
                Use AI to expand coverage.
              </h2>

              <p className="mt-7 max-w-3xl text-lg leading-8 text-[var(--ink-soft)]">
                The current evidence does not say Hybrid wins every metric.
                It shows why bounded AI is an attractive architecture for
                financial reconciliation: reasoning can be introduced without
                making the model the final authority.
              </p>
            </div>

            <div className="border-l border-[var(--border)] pl-8">
              <DecisionStep
                number="01"
                title="CONTROL"
                text="Keep deterministic checks authoritative."
              />

              <DecisionStep
                number="02"
                title="REASON"
                text="Use AI only when interpretation adds value."
              />

              <DecisionStep
                number="03"
                title="VERIFY"
                text="Require evidence before authorization."
              />
            </div>
          </div>

          <div className="mt-12 flex flex-col gap-4 border-t border-[var(--border)] pt-7 sm:flex-row sm:items-center sm:justify-between">
            <span className="font-mono text-[9px] font-semibold tracking-[0.16em] text-[var(--ink-muted)]">
              LEDGERSYNC · EVALUATION
            </span>

            <div className="flex flex-wrap gap-2">
              <Link
                href="/engineering"
                className="group inline-flex items-center gap-3 border border-[var(--navy)] bg-[var(--navy)] px-5 py-3 font-mono text-[9px] font-semibold tracking-[0.13em] text-white transition-all hover:-translate-y-px hover:bg-[var(--copper-dark)]"
              >
                OPEN ENGINEERING
                <span className="transition-transform group-hover:translate-x-1">
                  →
                </span>
              </Link>

              <Link
                href="/exceptions"
                className="inline-flex items-center gap-3 border border-[var(--copper)] px-5 py-3 font-mono text-[9px] font-semibold tracking-[0.13em] text-[var(--copper-dark)] transition-colors hover:bg-[var(--copper-soft)]"
              >
                INSPECT EXCEPTIONS
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="flex flex-col gap-3 border-t border-[var(--border)] py-7 font-mono text-[9px] tracking-[0.08em] text-[var(--ink-muted)] sm:flex-row sm:justify-between">
        <span>
          CURRENT HYBRID · 400 RECORDS · 0 FAILURES
        </span>

        <span>
          HISTORICAL COMPARISON SHOWN SEPARATELY
        </span>
      </footer>
    </main>
  );
}

/* =============================================================
   SUPPORTING COMPONENTS
   ============================================================= */

function Argument({
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
  return (
    <div className="border-b border-[var(--border)] pb-6">
      <div
        className={`font-mono text-[9px] font-semibold tracking-[0.14em] ${toneText(tone)}`}
      >
        {label}
      </div>

      <div className="mt-2 text-lg font-semibold">
        {value}
      </div>

      <p className="mt-2 text-sm leading-6 text-[var(--ink-muted)]">
        {detail}
      </p>
    </div>
  );
}

function CurrentMetric({
  value,
  label,
  detail,
  tone,
}: {
  value: string;
  label: string;
  detail: string;
  tone: Tone;
}) {
  return (
    <div>
      <div
        className={`mb-5 h-1.5 w-10 ${toneFill(tone)}`}
      />

      <div className="font-mono text-3xl font-medium tracking-[-0.04em] sm:text-4xl">
        {value}
      </div>

      <div className="mt-3 font-mono text-[9px] font-semibold tracking-[0.14em] text-[var(--ink-soft)]">
        {label}
      </div>

      <div className="mt-2 text-sm leading-6 text-[var(--ink-muted)]">
        {detail}
      </div>
    </div>
  );
}

function Interpretation({
  number,
  title,
  detail,
  tone,
}: {
  number: string;
  title: string;
  detail: string;
  tone: Tone;
}) {
  return (
    <div className="border-l-2 border-[var(--border-strong)] pl-4">
      <div className="font-mono text-[9px] text-[var(--ink-muted)]">
        {number}
      </div>

      <div
        className={`mt-2 font-mono text-2xl font-semibold tracking-[-0.03em] ${toneText(tone)}`}
      >
        {title}
      </div>

      <div className="mt-1 text-sm leading-6 text-[var(--ink-muted)]">
        {detail}
      </div>
    </div>
  );
}

function ScoreValue({
  value,
  tone,
  danger = false,
}: {
  value: string;
  tone: "rules" | "llm" | "hybrid";
  danger?: boolean;
}) {
  const color = danger
    ? "text-[var(--red)]"
    : tone === "hybrid"
      ? "text-[var(--lime)]"
      : tone === "llm"
        ? "text-[var(--blue)]"
        : "text-[var(--copper-dark)]";

  return (
    <span
      className={`font-mono text-lg font-semibold tracking-[-0.02em] ${color}`}
    >
      {value}
    </span>
  );
}

function Callout({
  label,
  text,
  tone,
}: {
  label: string;
  text: string;
  tone: Tone;
}) {
  return (
    <div className="border-l-2 border-[var(--border-strong)] pl-5">
      <div
        className={`font-mono text-[9px] font-semibold tracking-[0.14em] ${toneText(tone)}`}
      >
        {label}
      </div>

      <p className="mt-2 text-sm leading-6 text-[var(--ink-muted)]">
        {text}
      </p>
    </div>
  );
}

function ScenarioValue({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: Tone;
}) {
  return (
    <div>
      <div
        className={`font-mono text-[8px] font-semibold tracking-[0.12em] ${toneText(tone)}`}
      >
        {label}
      </div>

      <div className="mt-2 font-mono text-xl font-semibold tracking-[-0.03em]">
        {value}
      </div>
    </div>
  );
}

function ArchitectureValue({
  value,
  highlight = false,
}: {
  value: string;
  highlight?: boolean;
}) {
  const muted =
    value === "LOW" ||
    value === "LIMITED" ||
    value === "VARIABLE" ||
    value === "NONE";

  return (
    <span
      className={[
        "font-mono text-[10px] font-semibold tracking-[0.11em]",
        highlight
          ? "text-[var(--lime)]"
          : muted
            ? "text-[var(--ink-muted)]"
            : "text-[var(--ink-soft)]",
      ].join(" ")}
    >
      {value}
    </span>
  );
}

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
  return (
    <div>
      <div className="mb-2.5 flex items-center justify-between">
        <span className="font-mono text-[10px] font-semibold tracking-[0.13em] text-[var(--ink-soft)]">
          {label}
        </span>

        <span className="font-mono text-base font-semibold">
          {value}
        </span>
      </div>

      <div className="h-3 bg-[var(--surface-muted)]">
        <div
          className={`h-full ${
            tone === "blue"
              ? "bg-[var(--blue)]"
              : "bg-[var(--copper)]"
          }`}
          style={{ width }}
        />
      </div>
    </div>
  );
}

function DecisionStep({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (
    <div className="border-b border-[var(--border)] py-5 first:pt-0 last:border-b-0">
      <div className="flex items-center gap-3">
        <span className="font-mono text-[8px] text-[var(--copper-dark)]">
          {number}
        </span>

        <span className="font-mono text-[9px] font-semibold tracking-[0.14em]">
          {title}
        </span>
      </div>

      <div className="mt-2 text-base leading-6 text-[var(--ink-muted)]">
        {text}
      </div>
    </div>
  );
}