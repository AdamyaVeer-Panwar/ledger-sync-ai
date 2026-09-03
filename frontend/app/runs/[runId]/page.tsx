import Link from "next/link";

type RunSummaryPageProps = {
  params: Promise<{
    runID: string;
  }>;
};

const summaryMetrics = [
  {
    value: "400",
    label: "PROCESSED",
    detail: "records evaluated",
    tone: "copper",
  },
  {
    value: "304",
    label: "AUTO-MATCHED",
    detail: "76.0% automation",
    tone: "lime",
  },
  {
    value: "96",
    label: "HUMAN REVIEW",
    detail: "24.0% escalated",
    tone: "amber",
  },
  {
    value: "0",
    label: "UNRESOLVED",
    detail: "no unresolved output",
    tone: "blue",
  },
] as const;

const qualityMetrics = [
  ["76.00%", "RESOLUTION ACCURACY"],
  ["100.00%", "AUTO-MATCH PRECISION"],
  ["89.41%", "AUTO-MATCH RECALL"],
  ["0.00%", "FALSE AUTO-MATCH RATE"],
] as const;

const operationsMetrics = [
  ["90", "LLM INVOCATIONS"],
  ["22.50%", "LLM INVOCATION RATE"],
  ["78.01 ms", "P50 LATENCY"],
  ["11.51 s", "P95 LATENCY"],
] as const;

const decisions = [
  {
    label: "AUTO_MATCH",
    value: "304",
    percent: 76,
    tone: "lime",
  },
  {
    label: "HUMAN_REVIEW",
    value: "96",
    percent: 24,
    tone: "amber",
  },
  {
    label: "NO_MATCH",
    value: "0",
    percent: 0,
    tone: "neutral",
  },
] as const;

export default async function RunSummaryPage({
  params,
}: RunSummaryPageProps) {
  const { runID } = await params;

  return (
    <section className="mx-auto max-w-[1400px]">
      {/* =====================================================
          HEADER
          ===================================================== */}

      <div className="border-b border-[var(--border)] pb-7">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <span className="border border-[var(--blue)] bg-[var(--blue-soft)] px-2 py-1 font-mono text-[8px] font-semibold tracking-[0.16em] text-[var(--blue)]">
                02
              </span>

              <span className="font-mono text-[9px] font-semibold tracking-[0.2em] text-[var(--ink-muted)]">
                RUN SUMMARY
              </span>
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-4">
              <h1 className="text-4xl font-semibold tracking-[-0.05em] text-[var(--ink)] sm:text-5xl">
                {runID}
              </h1>

              <span className="flex items-center gap-2 border border-[var(--lime)] bg-[var(--lime-soft)] px-3 py-2 font-mono text-[8px] font-semibold tracking-[0.14em] text-[var(--lime)]">
                <span className="h-2 w-2 rounded-full bg-[var(--lime)]" />
                COMPLETED
              </span>
            </div>

            <p className="mt-3 text-sm text-[var(--ink-muted)]">
              Hybrid reconciliation · synthetic benchmark
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Link
              href="/exceptions"
              className="border border-[var(--border-strong)] bg-[var(--surface)] px-4 py-3 font-mono text-[9px] font-semibold tracking-[0.13em] text-[var(--ink)] transition-colors hover:border-[var(--amber)] hover:bg-[var(--amber-soft)]"
            >
              REVIEW EXCEPTIONS →
            </Link>

            <Link
              href="/evaluation"
              className="border border-[var(--border-strong)] bg-[var(--surface)] px-4 py-3 font-mono text-[9px] font-semibold tracking-[0.13em] text-[var(--ink)] transition-colors hover:border-[var(--blue)] hover:bg-[var(--blue-soft)]"
            >
              VIEW EVALUATION →
            </Link>
          </div>
        </div>
      </div>

      {/* =====================================================
          PRIMARY OUTCOME
          ===================================================== */}

      <div className="mt-6 grid border border-[var(--border)] bg-[var(--surface)] sm:grid-cols-2 lg:grid-cols-4">
        {summaryMetrics.map(
          (metric, index) => (
            <div
              key={metric.label}
              className={[
                "p-6",
                index < 3
                  ? "border-b border-[var(--border)] lg:border-b-0 lg:border-r"
                  : "",
              ].join(" ")}
            >
              <AccentLine tone={metric.tone} />

              <div className="font-mono text-3xl font-medium tracking-[-0.04em] text-[var(--ink)]">
                {metric.value}
              </div>

              <div className="mt-2 font-mono text-[8px] font-semibold tracking-[0.16em] text-[var(--ink-soft)]">
                {metric.label}
              </div>

              <div className="mt-1.5 text-xs text-[var(--ink-muted)]">
                {metric.detail}
              </div>
            </div>
          ),
        )}
      </div>

      {/* =====================================================
          BUSINESS OUTCOME + TELEMETRY
          ===================================================== */}

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
        {/* Automation safety */}

        <div className="overflow-hidden border border-[var(--border-dark)] bg-[var(--navy)] text-white">
          <div className="border-b border-[#35485F] px-6 py-5">
            <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[#91A1B1]">
              AUTOMATION SAFETY
            </div>

            <div className="mt-1 text-sm text-[#B7C1CB]">
              Quality of automated financial decisions
            </div>
          </div>

          <div className="grid sm:grid-cols-2">
            <SafetyMetric
              value="100.00%"
              label="AUTO-MATCH PRECISION"
              description="Every automatic match was correct in the benchmark."
              tone="lime"
            />

            <SafetyMetric
              value="0.00%"
              label="FALSE AUTO-MATCH"
              description="No incorrect automatic authorization was observed."
              tone="copper"
            />

            <SafetyMetric
              value="89.41%"
              label="AUTO-MATCH RECALL"
              description="Share of eligible matches successfully automated."
              tone="blue"
            />

            <SafetyMetric
              value="24.00%"
              label="HUMAN REVIEW"
              description="Ambiguous cases remain explicitly visible."
              tone="amber"
            />
          </div>

          <div className="border-t border-[#35485F] px-6 py-5">
            <div className="font-mono text-[8px] tracking-[0.12em] text-[#8190A0]">
              BENCHMARK QUALIFIER
            </div>

            <p className="mt-2 text-xs leading-5 text-[#AEB9C4]">
              Measurements are from the current synthetic evaluation dataset
              and should not be interpreted as production accuracy.
            </p>
          </div>
        </div>

        {/* Telemetry */}

        <div className="border border-[var(--border)] bg-[var(--surface)]">
          <PanelHeader
            label="OPERATIONAL TELEMETRY"
            detail="Observed during benchmark execution"
          />

          <div className="grid sm:grid-cols-2">
            {operationsMetrics.map(
              ([value, label], index) => (
                <div
                  key={label}
                  className={[
                    "p-6",
                    index % 2 === 0
                      ? "sm:border-r sm:border-[var(--border)]"
                      : "",
                    index < 2
                      ? "border-b border-[var(--border)]"
                      : "",
                  ].join(" ")}
                >
                  <div className="font-mono text-2xl font-medium tracking-[-0.035em] text-[var(--ink)]">
                    {value}
                  </div>

                  <div className="mt-2 font-mono text-[8px] font-semibold tracking-[0.15em] text-[var(--ink-muted)]">
                    {label}
                  </div>
                </div>
              ),
            )}
          </div>

          <div className="border-t border-[var(--border)] bg-[var(--surface-soft)] px-6 py-5">
            <div className="flex items-center justify-between gap-4">
              <span className="font-mono text-[8px] font-semibold tracking-[0.14em] text-[var(--ink-muted)]">
                TOTAL BENCHMARK TIME
              </span>

              <span className="font-mono text-sm font-semibold text-[var(--ink)]">
                804.35 s
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* =====================================================
          DECISION DISTRIBUTION
          ===================================================== */}

      <div className="mt-6 border border-[var(--border)] bg-[var(--surface)]">
        <PanelHeader
          label="DECISION DISTRIBUTION"
          detail="Final reconciliation outcomes"
        />

        <div className="p-6 sm:p-8">
          <div className="space-y-7">
            {decisions.map(
              (decision) => (
                <DecisionBar
                  key={decision.label}
                  label={decision.label}
                  value={decision.value}
                  percent={decision.percent}
                  tone={decision.tone}
                />
              ),
            )}
          </div>

          <div className="mt-8 border-t border-[var(--border)] pt-6">
            <div className="flex flex-wrap gap-6 font-mono text-[8px] tracking-[0.13em] text-[var(--ink-muted)]">
              <LegendDot
                color="bg-[var(--lime)]"
                label="AUTOMATION"
              />

              <LegendDot
                color="bg-[var(--amber)]"
                label="HUMAN ATTENTION"
              />

              <LegendDot
                color="bg-[var(--border-strong)]"
                label="NO MATCH"
              />
            </div>
          </div>
        </div>
      </div>

      {/* =====================================================
          QUALITY
          ===================================================== */}

      <div className="mt-6 border border-[var(--border)] bg-[var(--surface)]">
        <PanelHeader
          label="RESOLUTION QUALITY"
          detail="Measured outcome of the hybrid engine"
        />

        <div className="grid sm:grid-cols-2 lg:grid-cols-4">
          {qualityMetrics.map(
            ([value, label], index) => (
              <div
                key={label}
                className={[
                  "p-6",
                  index < 3
                    ? "border-b border-[var(--border)] lg:border-b-0 lg:border-r"
                    : "",
                ].join(" ")}
              >
                <div className="font-mono text-2xl font-medium tracking-[-0.035em] text-[var(--ink)]">
                  {value}
                </div>

                <div className="mt-2 font-mono text-[8px] font-semibold tracking-[0.14em] text-[var(--ink-muted)]">
                  {label}
                </div>
              </div>
            ),
          )}
        </div>
      </div>

      {/* =====================================================
          ENGINEERING INTERPRETATION
          ===================================================== */}

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="relative overflow-hidden border border-[var(--copper)] bg-[var(--copper-soft)] p-6 sm:p-8">
          <div className="absolute right-0 top-0 h-full w-1 bg-[var(--copper)]" />

          <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--copper-dark)]">
            ENGINEERING INTERPRETATION
          </div>

          <h2 className="mt-4 max-w-lg text-2xl font-semibold tracking-[-0.035em] text-[var(--ink)] sm:text-3xl">
            Automation is earned by evidence.
          </h2>

          <p className="mt-4 max-w-xl text-sm leading-6 text-[var(--ink-soft)]">
            The benchmark shows a system that automates a substantial portion
            of the workload while preserving ambiguous cases for human review.
            The model is a reasoning component, not the final authority.
          </p>

          <div className="mt-6 font-mono text-[9px] font-semibold tracking-[0.12em] text-[var(--copper-dark)]">
            PROPOSE → VERIFY → AUTHORIZE
          </div>
        </div>

        <div className="border border-[var(--border)] bg-[var(--surface-soft)] p-6 sm:p-8">
          <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--ink-muted)]">
            NEXT INVESTIGATION
          </div>

          <h2 className="mt-4 text-2xl font-semibold tracking-[-0.035em] text-[var(--ink)]">
            Inspect the 96 review cases.
          </h2>

          <p className="mt-4 text-sm leading-6 text-[var(--ink-muted)]">
            A good reconciliation engine does not hide uncertainty. Open an
            exception to inspect candidates, evidence, confidence, and why
            automation was withheld.
          </p>

          <Link
            href="/exceptions"
            className="mt-6 inline-flex items-center gap-3 bg-[var(--navy)] px-5 py-3 font-mono text-[9px] font-semibold tracking-[0.14em] text-white transition-colors hover:bg-[var(--navy-2)]"
          >
            OPEN EXCEPTION QUEUE
            <span>→</span>
          </Link>
        </div>
      </div>

      {/* =====================================================
          FOOTER
          ===================================================== */}

      <div className="flex flex-col gap-2 border-t border-[var(--border)] py-6 font-mono text-[8px] tracking-[0.08em] text-[var(--ink-muted)] sm:flex-row sm:items-center sm:justify-between">
        <span>
          {runID} · SYNTHETIC BENCHMARK · HYBRID RESOLUTION
        </span>

        <Link
          href="/engineering"
          className="text-[var(--ink-soft)] underline decoration-[var(--copper)] underline-offset-4 hover:text-[var(--copper-dark)]"
        >
          ENGINEERING REPORT →
        </Link>
      </div>
    </section>
  );
}

/* =============================================================
   PANEL HEADER
   ============================================================= */

function PanelHeader({
  label,
  detail,
}: {
  label: string;
  detail: string;
}) {
  return (
    <div className="flex flex-col gap-1 border-b border-[var(--border)] px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
      <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--ink-soft)]">
        {label}
      </div>

      <div className="text-xs text-[var(--ink-muted)]">
        {detail}
      </div>
    </div>
  );
}

/* =============================================================
   ACCENT LINE
   ============================================================= */

function AccentLine({
  tone,
}: {
  tone:
    | "copper"
    | "blue"
    | "lime"
    | "amber";
}) {
  const color =
    tone === "copper"
      ? "bg-[var(--copper)]"
      : tone === "blue"
        ? "bg-[var(--blue)]"
        : tone === "lime"
          ? "bg-[var(--lime)]"
          : "bg-[var(--amber)]";

  return (
    <div
      className={`mb-4 h-1 w-8 ${color}`}
      aria-hidden="true"
    />
  );
}

/* =============================================================
   SAFETY METRIC
   ============================================================= */

function SafetyMetric({
  value,
  label,
  description,
  tone,
}: {
  value: string;
  label: string;
  description: string;
  tone:
    | "lime"
    | "copper"
    | "blue"
    | "amber";
}) {
  const valueColor =
    tone === "lime"
      ? "text-[var(--lime)]"
      : tone === "copper"
        ? "text-[var(--copper)]"
        : tone === "blue"
          ? "text-[#76B9D0]"
          : "text-[#D4A45A]";

  return (
    <div className="border-b border-[#35485F] p-6">
      <div
        className={`font-mono text-3xl font-medium ${valueColor}`}
      >
        {value}
      </div>

      <div className="mt-2 font-mono text-[8px] font-semibold tracking-[0.15em] text-white">
        {label}
      </div>

      <p className="mt-3 text-xs leading-5 text-[#8F9EAD]">
        {description}
      </p>
    </div>
  );
}

/* =============================================================
   DECISION BAR
   ============================================================= */

function DecisionBar({
  label,
  value,
  percent,
  tone,
}: {
  label: string;
  value: string;
  percent: number;
  tone:
    | "lime"
    | "amber"
    | "neutral";
}) {
  const barColor =
    tone === "lime"
      ? "bg-[var(--lime)]"
      : tone === "amber"
        ? "bg-[var(--amber)]"
        : "bg-[var(--border-strong)]";

  const labelColor =
    tone === "lime"
      ? "text-[var(--lime)]"
      : tone === "amber"
        ? "text-[var(--amber)]"
        : "text-[var(--ink-muted)]";

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-4">
        <span
          className={`font-mono text-[9px] font-semibold tracking-[0.15em] ${labelColor}`}
        >
          {label}
        </span>

        <div className="flex items-center gap-3">
          <span className="font-mono text-xs font-semibold text-[var(--ink)]">
            {value}
          </span>

          <span className="font-mono text-[8px] text-[var(--ink-muted)]">
            {percent.toFixed(1)}%
          </span>
        </div>
      </div>

      <div className="h-2 w-full overflow-hidden bg-[var(--surface-muted)]">
        <div
          className={`h-full ${barColor}`}
          style={{
            width: `${percent}%`,
          }}
        />
      </div>
    </div>
  );
}

/* =============================================================
   LEGEND DOT
   ============================================================= */

function LegendDot({
  color,
  label,
}: {
  color: string;
  label: string;
}) {
  return (
    <span className="flex items-center gap-2">
      <span className={`h-2 w-2 rounded-full ${color}`} />
      {label}
    </span>
  );
}