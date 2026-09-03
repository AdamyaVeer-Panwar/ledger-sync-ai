import Link from "next/link";

const metrics = [
  ["400", "RECORDS", "Benchmark scope", "copper"],
  ["76.0%", "AUTOMATION", "304 auto-matched", "blue"],
  ["100%", "AUTO-MATCH PRECISION", "0 false auto-matches", "lime"],
  ["22.5%", "LLM INVOCATION", "90 invocations", "amber"],
] as const;

const stages = [
  ["01", "INGEST", "Settlement + ledger data", "neutral"],
  ["02", "RETRIEVE", "Bounded candidates", "neutral"],
  ["03", "RULES", "Deterministic evidence", "copper"],
  ["04", "VERIFY", "Evidence before action", "lime"],
  ["05", "POLICY", "Match · Review · No match", "navy"],
] as const;

export default function HomePage() {
  return (
    <div className="technical-grid min-h-[calc(100vh-150px)]">
      {/* =======================================================
          HERO
          ======================================================= */}

      <section className="overflow-hidden border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow-sm)]">
        <div className="grid lg:grid-cols-[1.45fr_.55fr]">
          <div className="relative border-b border-[var(--border)] p-7 sm:p-10 lg:border-b-0 lg:border-r lg:p-12 xl:p-14">
            <div className="absolute left-0 top-0 h-1 w-24 bg-[var(--copper)]" />

            <div className="flex items-center gap-3">
              <span className="border border-[var(--copper)] bg-[var(--copper-soft)] px-2 py-1 font-mono text-[8px] font-semibold tracking-[0.14em] text-[var(--copper-dark)]">
                CONTROL
              </span>

              <span className="font-mono text-[9px] tracking-[0.2em] text-[var(--ink-muted)]">
                FINANCIAL RECONCILIATION ENGINE
              </span>
            </div>

            <h1 className="mt-8 max-w-4xl text-5xl font-semibold leading-[0.94] tracking-[-0.055em] text-[var(--ink)] sm:text-6xl xl:text-[78px]">
              Automate what can be proven.
              <span className="mt-2 block text-[var(--ink-muted)]">
                Escalate what cannot.
              </span>
            </h1>

            <p className="mt-8 max-w-2xl text-base leading-7 text-[var(--ink-soft)]">
              A reconciliation control layer for settlement operations:
              deterministic evidence first, bounded AI reasoning second,
              verification before authorization.
            </p>

            <div className="mt-9 flex flex-wrap gap-3">
              <Link
                href="/run"
                className="group inline-flex items-center gap-4 bg-[var(--copper)] px-6 py-4 font-mono text-[10px] font-semibold tracking-[0.15em] text-white shadow-[var(--shadow-sm)] transition-all hover:-translate-y-px hover:bg-[var(--copper-dark)]"
              >
                START A RUN
                <span className="transition-transform group-hover:translate-x-1">
                  →
                </span>
              </Link>

              <Link
                href="/engineering"
                className="inline-flex items-center gap-4 border border-[var(--navy)] bg-transparent px-6 py-4 font-mono text-[10px] font-semibold tracking-[0.15em] text-[var(--navy)] transition-colors hover:bg-[var(--navy)] hover:text-white"
              >
                WHY HYBRID
              </Link>
            </div>

            <div className="mt-10 flex flex-wrap gap-x-8 gap-y-3 border-t border-[var(--border)] pt-5 font-mono text-[8px] tracking-[0.15em] text-[var(--ink-muted)]">
              <span>RULES FIRST</span>
              <span>AI BOUNDED</span>
              <span>VERIFY BEFORE ACTION</span>
              <span>HUMAN ESCALATION</span>
            </div>
          </div>

          {/* =====================================================
              DECISION CONTROL
              ===================================================== */}

          <div className="bg-[var(--navy)] p-7 text-[var(--ink-inverse)] sm:p-10">
            <div className="flex items-center justify-between border-b border-[#34485E] pb-5">
              <span className="font-mono text-[8px] tracking-[0.2em] text-[#91A1B1]">
                DECISION CONTROL
              </span>

              <span className="font-mono text-[8px] tracking-[0.15em] text-[var(--lime)]">
                EVIDENCE LED
              </span>
            </div>

            <div className="py-9">
              <ControlBlock
                number="01"
                label="LLM"
                value="PROPOSAL"
                tone="copper"
              />

              <div className="ml-3 h-9 border-l border-[#4D5F73]" />

              <ControlBlock
                number="02"
                label="VERIFIER"
                value="EVIDENCE"
                tone="blue"
              />

              <div className="ml-3 h-9 border-l border-[#4D5F73]" />

              <ControlBlock
                number="03"
                label="POLICY"
                value="ACTION"
                tone="lime"
              />
            </div>

            <div className="border-t border-[#34485E] pt-6">
              <div className="font-mono text-[10px] leading-6 text-white">
                AI can reason.
                <br />
                <span className="text-[#8C9BAA]">
                  Evidence decides.
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* =====================================================
            BENCHMARK METRICS
            ===================================================== */}

        <div className="grid border-t border-[var(--border)] sm:grid-cols-2 lg:grid-cols-4">
          {metrics.map(
            ([value, label, detail, tone], index) => (
              <div
                key={label}
                className={[
                  "bg-[var(--surface-strong)] p-6",
                  index < 3
                    ? "border-b border-[var(--border)] lg:border-b-0 lg:border-r"
                    : "",
                  index === 1
                    ? "sm:border-r sm:border-[var(--border)] lg:border-r"
                    : "",
                ].join(" ")}
              >
                <MetricAccent tone={tone} />

                <div className="font-mono text-3xl font-medium tracking-[-0.04em]">
                  {value}
                </div>

                <div className="mt-2 font-mono text-[8px] font-semibold tracking-[0.16em] text-[var(--ink-soft)]">
                  {label}
                </div>

                <div className="mt-1.5 text-xs text-[var(--ink-muted)]">
                  {detail}
                </div>
              </div>
            ),
          )}
        </div>
      </section>

      {/* =======================================================
          SYSTEM MODEL + RECONCILIATION PIPELINE
          ======================================================= */}

      <section className="mt-6 grid gap-6 lg:grid-cols-[0.72fr_1.28fr]">
        {/* System model */}

        <div className="relative overflow-hidden border border-[var(--border-dark)] bg-[var(--navy)] p-7 text-white sm:p-9">
          <div className="absolute right-0 top-0 h-full w-px bg-[var(--copper)] opacity-60" />

          <div className="font-mono text-[8px] tracking-[0.2em] text-[#92A1B0]">
            SYSTEM MODEL
          </div>

          <h2 className="mt-4 max-w-md text-3xl font-semibold leading-tight tracking-[-0.04em]">
            Reasoning is not authorization.
          </h2>

          <p className="mt-5 max-w-md text-sm leading-6 text-[#AAB6C2]">
            The model can help interpret ambiguity, but verified evidence and
            policy remain between a suggestion and a financial action.
          </p>

          <div className="mt-9 border-t border-[#34485E] pt-6">
            <div className="font-mono text-[9px] tracking-[0.13em] text-[#8190A0]">
              CONTROL PRINCIPLE
            </div>

            <div className="mt-3 font-mono text-[10px] tracking-[0.14em] text-white">
              PROPOSE
              <span className="mx-2 text-[var(--copper)]">→</span>
              VERIFY
              <span className="mx-2 text-[var(--copper)]">→</span>
              AUTHORIZE
            </div>
          </div>
        </div>

        {/* =====================================================
            RECONCILIATION PIPELINE
            ===================================================== */}

        <div className="overflow-hidden border border-[var(--border)] bg-[var(--surface)]">
          <div className="flex items-center justify-between border-b border-[var(--border)] px-6 py-5">
            <div>
              <div className="font-mono text-[8px] tracking-[0.2em] text-[var(--ink-muted)]">
                RECONCILIATION PIPELINE
              </div>

              <div className="mt-1 text-xs text-[var(--ink-muted)]">
                Controlled decision flow
              </div>
            </div>

            <div className="hidden font-mono text-[8px] font-medium tracking-[0.15em] text-[var(--copper-dark)] sm:block">
              EVIDENCE → ACTION
            </div>
          </div>

          <div className="relative p-6 sm:p-8">
            {/* Continuous rail on desktop */}

            <div className="absolute left-[11%] right-[11%] top-[79px] hidden h-px bg-[var(--border-strong)] lg:block" />

            <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-5">
              {stages.map(
                ([number, title, detail, tone]) => (
                  <PipelineStage
                    key={number}
                    number={number}
                    title={title}
                    detail={detail}
                    tone={tone}
                  />
                ),
              )}
            </div>

            {/* -------------------------------------------------
                AI branch
                ------------------------------------------------- */}

            <div className="mt-8 border-t border-[var(--border)] pt-6">
              <div className="grid gap-5 lg:grid-cols-[1fr_auto] lg:items-center">
                <div>
                  <div className="font-mono text-[8px] tracking-[0.18em] text-[var(--ink-muted)]">
                    WHEN DETERMINISTIC EVIDENCE IS INSUFFICIENT
                  </div>

                  <div className="mt-3 flex flex-wrap items-center gap-2 font-mono text-[9px] tracking-[0.12em]">
                    <span className="border border-[var(--blue)] bg-[var(--blue-soft)] px-3 py-2 font-semibold text-[var(--blue)]">
                      AI RESOLUTION
                    </span>

                    <span className="text-[var(--ink-muted)]">
                      →
                    </span>

                    <span className="border border-[var(--lime)] bg-[var(--lime-soft)] px-3 py-2 font-semibold text-[var(--lime)]">
                      DETERMINISTIC VERIFICATION
                    </span>
                  </div>
                </div>

                <div className="max-w-xs text-xs leading-5 text-[var(--ink-muted)] lg:text-right">
                  AI expands reasoning coverage without receiving final
                  authority.
                </div>
              </div>
            </div>

            {/* -------------------------------------------------
                Terminal-style outcome rail
                ------------------------------------------------- */}

            <div className="mt-6 grid gap-px border border-[var(--border)] bg-[var(--border)] sm:grid-cols-3">
              <div className="bg-[var(--surface-soft)] px-4 py-4">
                <div className="font-mono text-[8px] tracking-[0.15em] text-[var(--ink-muted)]">
                  DETERMINISTIC
                </div>

                <div className="mt-2 font-mono text-[10px] font-semibold text-[var(--copper-dark)]">
                  PROVEN → AUTOMATE
                </div>
              </div>

              <div className="bg-[var(--surface-soft)] px-4 py-4">
                <div className="font-mono text-[8px] tracking-[0.15em] text-[var(--ink-muted)]">
                  AMBIGUOUS
                </div>

                <div className="mt-2 font-mono text-[10px] font-semibold text-[var(--amber)]">
                  REVIEW → HUMAN
                </div>
              </div>

              <div className="bg-[var(--surface-soft)] px-4 py-4">
                <div className="font-mono text-[8px] tracking-[0.15em] text-[var(--ink-muted)]">
                  UNSUPPORTED
                </div>

                <div className="mt-2 font-mono text-[10px] font-semibold text-[var(--red)]">
                  NO MATCH → STOP
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =======================================================
          REVIEW PATH
          ======================================================= */}

      <section className="mt-6 border border-[var(--border)] bg-[var(--surface-strong)] p-6 sm:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="font-mono text-[8px] tracking-[0.2em] text-[var(--ink-muted)]">
              REVIEW PATH
            </div>

            <h2 className="mt-2 text-2xl font-semibold tracking-[-0.03em] text-[var(--ink)]">
              See what happened. Then ask why.
            </h2>
          </div>

          <div className="flex flex-wrap gap-3">
            <Link
              href="/run"
              className="border border-[var(--border-strong)] px-4 py-3 font-mono text-[9px] font-semibold tracking-[0.13em] transition-colors hover:border-[var(--copper)] hover:bg-[var(--copper-soft)]"
            >
              01 · RUN
            </Link>

            <Link
              href="/exceptions"
              className="border border-[var(--border-strong)] px-4 py-3 font-mono text-[9px] font-semibold tracking-[0.13em] transition-colors hover:border-[var(--amber)] hover:bg-[var(--amber-soft)]"
            >
              02 · EXCEPTIONS
            </Link>

            <Link
              href="/evaluation"
              className="border border-[var(--border-strong)] px-4 py-3 font-mono text-[9px] font-semibold tracking-[0.13em] transition-colors hover:border-[var(--blue)] hover:bg-[var(--blue-soft)]"
            >
              03 · EVALUATION
            </Link>
          </div>
        </div>
      </section>

      {/* =======================================================
          HONESTY FOOTER
          ======================================================= */}

      <div className="flex flex-col gap-2 py-6 font-mono text-[8px] tracking-[0.08em] text-[var(--ink-muted)] sm:flex-row sm:justify-between">
        <span>
          CURRENT RESULTS · SYNTHETIC BENCHMARK · NOT LIVE FINANCIAL DATA
        </span>

        <Link
          href="/engineering"
          className="text-[var(--ink-soft)] underline decoration-[var(--copper)] underline-offset-4 transition-colors hover:text-[var(--copper-dark)]"
        >
          ENGINEERING REPORT →
        </Link>
      </div>
    </div>
  );
}

/* =============================================================
   PIPELINE STAGE
   ============================================================= */

function PipelineStage({
  number,
  title,
  detail,
  tone,
}: {
  number: string;
  title: string;
  detail: string;
  tone: "neutral" | "copper" | "lime" | "navy";
}) {
  const dotClass =
    tone === "copper"
      ? "bg-[var(--copper)]"
      : tone === "lime"
        ? "bg-[var(--lime)]"
        : tone === "navy"
          ? "bg-[var(--navy)]"
          : "bg-[var(--border-strong)]";

  const titleClass =
    tone === "copper"
      ? "text-[var(--copper-dark)]"
      : tone === "lime"
        ? "text-[var(--lime)]"
        : "text-[var(--ink)]";

  return (
    <div className="relative z-10 bg-[var(--surface)]">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[8px] tracking-[0.14em] text-[var(--ink-muted)]">
          {number}
        </span>

        <span
          className={`h-2.5 w-2.5 rounded-full ${dotClass}`}
        />
      </div>

      <div
        className={`mt-7 font-mono text-[9px] font-semibold tracking-[0.15em] ${titleClass}`}
      >
        {title}
      </div>

      <p className="mt-2 max-w-[150px] text-xs leading-5 text-[var(--ink-muted)]">
        {detail}
      </p>
    </div>
  );
}

/* =============================================================
   METRIC ACCENT
   ============================================================= */

function MetricAccent({
  tone,
}: {
  tone: "copper" | "blue" | "lime" | "amber";
}) {
  const colorClass =
    tone === "copper"
      ? "bg-[var(--copper)]"
      : tone === "blue"
        ? "bg-[var(--blue)]"
        : tone === "lime"
          ? "bg-[var(--lime)]"
          : "bg-[var(--amber)]";

  return (
    <div
      className={`mb-4 h-1 w-8 ${colorClass}`}
      aria-hidden="true"
    />
  );
}

/* =============================================================
   DECISION CONTROL BLOCK
   ============================================================= */

function ControlBlock({
  number,
  label,
  value,
  tone,
}: {
  number: string;
  label: string;
  value: string;
  tone: "copper" | "blue" | "lime";
}) {
  const valueClass =
    tone === "copper"
      ? "text-[var(--copper)]"
      : tone === "blue"
        ? "text-[#6FB6CF]"
        : "text-[var(--lime)]";

  return (
    <div className="flex items-center gap-4">
      <span className="font-mono text-[8px] text-[#6A7A8B]">
        {number}
      </span>

      <span className="font-mono text-[10px] font-semibold tracking-[0.14em] text-white">
        {label}
      </span>

      <span className="ml-auto font-mono text-[9px] tracking-[0.13em] text-[#8795A4]">
        →
      </span>

      <span
        className={`font-mono text-[9px] font-semibold tracking-[0.13em] ${valueClass}`}
      >
        {value}
      </span>
    </div>
  );
}