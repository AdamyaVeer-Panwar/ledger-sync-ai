"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { FileDropzone } from "@/components/ui/file-dropzone";
import { PipelineStatus } from "@/components/run/pipeline-status";

type PipelineStatusValue =
  | "pending"
  | "active"
  | "complete";

type PipelineStep = {
  label: string;
  description: string;
  status: PipelineStatusValue;
};

const PIPELINE_TEMPLATE: PipelineStep[] = [
  {
    label: "INGESTION",
    description: "Validate and normalize source records",
    status: "pending",
  },
  {
    label: "CANDIDATE RETRIEVAL",
    description: "Build a bounded candidate set",
    status: "pending",
  },
  {
    label: "RULE ENGINE",
    description: "Evaluate deterministic evidence",
    status: "pending",
  },
  {
    label: "AI RESOLUTION",
    description: "Invoke reasoning only when required",
    status: "pending",
  },
  {
    label: "VERIFICATION",
    description: "Validate the proposed resolution",
    status: "pending",
  },
  {
    label: "POLICY",
    description: "Authorize match, review, or no-match",
    status: "pending",
  },
  {
    label: "PERSISTENCE",
    description: "Store the reconciliation outcome",
    status: "pending",
  },
];

function createDemoRunId(): string {
  const suffix = Date.now()
    .toString()
    .slice(-6);

  return `DEMO-${suffix}`;
}

export default function RunPage() {
  const router = useRouter();

  const [settlementFile, setSettlementFile] =
    useState<File | null>(null);

  const [ledgerFile, setLedgerFile] =
    useState<File | null>(null);

  const [amountTolerance, setAmountTolerance] =
    useState("0.02");

  const [dateWindow, setDateWindow] =
    useState("2");

  const [candidateLimit, setCandidateLimit] =
    useState("50");

  const [pipeline, setPipeline] =
    useState<PipelineStep[]>(
      PIPELINE_TEMPLATE,
    );

  const [running, setRunning] =
    useState(false);

  const [completed, setCompleted] =
    useState(false);

  const [runMode, setRunMode] =
    useState<"demo" | "custom">("demo");

  const [runId, setRunId] =
    useState<string | null>(null);

  const filesReady =
    Boolean(settlementFile) &&
    Boolean(ledgerFile);

  const canRun =
    !running &&
    !completed &&
    (runMode === "demo" || filesReady);

  useEffect(() => {
    if (!running) {
      return;
    }

    let currentStep = 0;

    const timer = window.setInterval(() => {
      if (
        currentStep >=
        PIPELINE_TEMPLATE.length
      ) {
        window.clearInterval(timer);

        setPipeline(
          PIPELINE_TEMPLATE.map((step) => ({
            ...step,
            status: "complete",
          })),
        );

        setRunning(false);
        setCompleted(true);

        return;
      }

      setPipeline((current) =>
        current.map((step, index) => {
          if (index < currentStep) {
            return {
              ...step,
              status: "complete",
            };
          }

          if (index === currentStep) {
            return {
              ...step,
              status: "active",
            };
          }

          return {
            ...step,
            status: "pending",
          };
        }),
      );

      currentStep += 1;
    }, 650);

    return () => {
      window.clearInterval(timer);
    };
  }, [running]);

  function startRun() {
    if (!canRun) {
      return;
    }

    const newRunId =
      createDemoRunId();

    setRunId(newRunId);

    setPipeline(
      PIPELINE_TEMPLATE.map((step) => ({
        ...step,
        status: "pending",
      })),
    );

    setCompleted(false);
    setRunning(true);
  }

  function resetRun() {
    setSettlementFile(null);
    setLedgerFile(null);
    setRunId(null);

    setPipeline(
      PIPELINE_TEMPLATE.map((step) => ({
        ...step,
        status: "pending",
      })),
    );

    setRunning(false);
    setCompleted(false);
  }

  function viewSummary() {
    if (!runId) {
      return;
    }

    router.push(`/runs/${runId}`);
  }

  return (
    <section className="mx-auto max-w-[1400px]">
      {/* =====================================================
          HEADER
          ===================================================== */}

      <div className="mb-7 border-b border-[var(--border)] pb-7">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <span className="border border-[var(--copper)] bg-[var(--copper-soft)] px-2 py-1 font-mono text-[8px] font-semibold tracking-[0.16em] text-[var(--copper-dark)]">
                01
              </span>

              <span className="font-mono text-[9px] font-semibold tracking-[0.2em] text-[var(--copper-dark)]">
                RECONCILIATION RUN
              </span>
            </div>

            <h1 className="mt-4 text-4xl font-semibold tracking-[-0.05em] text-[var(--ink)] sm:text-5xl">
              Run reconciliation
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--ink-muted)]">
              Give LedgerSync settlement and ledger data, then observe the
              controlled path from evidence to decision.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="font-mono text-[8px] font-medium tracking-[0.14em] text-[var(--ink-muted)]">
              ENGINE
            </span>

            <span className="flex items-center gap-2 border border-[var(--lime)] bg-[var(--lime-soft)] px-3 py-2 font-mono text-[8px] font-semibold tracking-[0.14em] text-[var(--lime)]">
              <span className="h-2 w-2 rounded-full bg-[var(--lime)]" />
              READY
            </span>
          </div>
        </div>
      </div>

      {/* =====================================================
          RUN MODE
          ===================================================== */}

      <div className="mb-6 grid gap-3 border border-[var(--border)] bg-[var(--surface)] p-2 md:grid-cols-2">
        <ModeButton
          active={runMode === "demo"}
          label="DEMO RUN"
          detail="Use the existing 400-record synthetic benchmark"
          onClick={() => {
            if (!running) {
              setRunMode("demo");
              setCompleted(false);
            }
          }}
        />

        <ModeButton
          active={runMode === "custom"}
          label="CUSTOM RUN"
          detail="Upload your own settlement and ledger data"
          onClick={() => {
            if (!running) {
              setRunMode("custom");
              setCompleted(false);
            }
          }}
        />
      </div>

      {/* =====================================================
          DEMO CONTEXT
          ===================================================== */}

      {runMode === "demo" && (
        <div className="mb-6 grid gap-6 lg:grid-cols-[1.08fr_0.92fr]">
          <div className="relative overflow-hidden border border-[var(--copper)] bg-[var(--copper-soft)] p-6 sm:p-8">
            <div className="absolute right-0 top-0 h-full w-1 bg-[var(--copper)]" />

            <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--copper-dark)]">
              FASTEST REVIEW PATH
            </div>

            <h2 className="mt-4 max-w-xl text-2xl font-semibold leading-tight tracking-[-0.035em] text-[var(--ink)]">
              Run the complete benchmark without preparing files.
            </h2>

            <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--ink-soft)]">
              The demo uses LedgerSync&apos;s existing synthetic evaluation
              scenario set. No live financial data is used.
            </p>

            <div className="mt-6 flex flex-wrap gap-2">
              <InfoChip text="400 RECORDS" />
              <InfoChip text="10 SCENARIO TYPES" />
              <InfoChip text="REPRODUCIBLE" />
              <InfoChip text="SYNTHETIC DATA" />
            </div>
          </div>

          <div className="border border-[var(--border-dark)] bg-[var(--navy)] p-6 text-white sm:p-8">
            <div className="flex items-center justify-between">
              <div className="font-mono text-[8px] tracking-[0.2em] text-[#91A1B1]">
                EXPECTED BENCHMARK
              </div>

              <span className="font-mono text-[8px] tracking-[0.12em] text-[var(--copper)]">
                HYBRID
              </span>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-px border border-[#35485F] bg-[#35485F]">
              <DemoMetric
                value="304"
                label="AUTO MATCH"
                tone="lime"
              />

              <DemoMetric
                value="96"
                label="HUMAN REVIEW"
                tone="amber"
              />

              <DemoMetric
                value="90"
                label="LLM CALLS"
                tone="blue"
              />

              <DemoMetric
                value="0%"
                label="FALSE AUTO MATCH"
                tone="copper"
              />
            </div>
          </div>
        </div>
      )}

      {/* =====================================================
          MAIN WORKSPACE
          ===================================================== */}

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_390px]">
        <div className="space-y-6">
          {runMode === "custom" && (
            <div className="border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[var(--shadow-sm)] sm:p-8">
              <PanelHeading
                eyebrow="SOURCE DATA"
                title="Upload reconciliation inputs"
                description="Provide the settlement export and ledger export that should be reconciled."
              />

              <div className="mt-7 space-y-5">
                <FileDropzone
                  label="SETTLEMENT DATA"
                  description="Settlement export"
                  file={settlementFile}
                  onFileChange={setSettlementFile}
                />

                <FileDropzone
                  label="LEDGER DATA"
                  description="Ledger export"
                  file={ledgerFile}
                  onFileChange={setLedgerFile}
                />
              </div>
            </div>
          )}

          <div className="border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow-sm)]">
            <div className="border-b border-[var(--border)] p-6 sm:p-8">
              <div className="flex items-start justify-between gap-4">
                <PanelHeading
                  eyebrow="RUN PARAMETERS"
                  title="Resolution controls"
                  description="Bound the matching search and keep automation policy explicit."
                />

                <span className="hidden border border-[var(--border)] bg-[var(--surface-soft)] px-2.5 py-1.5 font-mono text-[8px] tracking-[0.12em] text-[var(--ink-muted)] sm:block">
                  CONFIG / V1
                </span>
              </div>

              <div className="mt-7 grid gap-5 sm:grid-cols-3">
                <ConfigField
                  label="AMOUNT TOLERANCE"
                  value={amountTolerance}
                  onChange={setAmountTolerance}
                />

                <ConfigField
                  label="DATE WINDOW"
                  value={dateWindow}
                  suffix="DAYS"
                  onChange={setDateWindow}
                />

                <ConfigField
                  label="CANDIDATE LIMIT"
                  value={candidateLimit}
                  onChange={setCandidateLimit}
                />
              </div>
            </div>

            <div className="grid gap-px border-t border-[var(--border)] bg-[var(--border)] sm:grid-cols-2">
              <ControlRow
                label="RULE ENGINE"
                value="ENABLED"
                tone="lime"
              />

              <ControlRow
                label="AI FALLBACK"
                value="BOUNDED"
                tone="blue"
              />

              <ControlRow
                label="VERIFICATION"
                value="REQUIRED"
                tone="lime"
              />

              <ControlRow
                label="HUMAN ESCALATION"
                value="ENABLED"
                tone="amber"
              />
            </div>
          </div>

          {/* =================================================
              ACTION AREA
              ================================================= */}

          <div className="border-t border-[var(--border)] pt-6">
            <div className="flex flex-col gap-3 sm:flex-row">
              <button
                type="button"
                onClick={startRun}
                disabled={!canRun}
                className={[
                  "group inline-flex items-center justify-center gap-4 px-6 py-4 font-mono text-[10px] font-semibold tracking-[0.15em] transition-all",
                  canRun
                    ? "bg-[var(--copper)] text-white shadow-[var(--shadow-sm)] hover:-translate-y-px hover:bg-[var(--copper-dark)]"
                    : "border border-[var(--border)] bg-[var(--surface-muted)] text-[var(--ink-muted)]",
                ].join(" ")}
              >
                {running
                  ? "PROCESSING RECONCILIATION"
                  : completed
                    ? "RUN COMPLETE"
                    : runMode === "demo"
                      ? "RUN 400-RECORD DEMO"
                      : "RUN RECONCILIATION"}

                {!running && !completed && (
                  <span className="transition-transform group-hover:translate-x-1">
                    →
                  </span>
                )}
              </button>

              {completed && (
                <>
                  <button
                    type="button"
                    onClick={viewSummary}
                    className="inline-flex items-center justify-center gap-3 bg-[var(--navy)] px-6 py-4 font-mono text-[10px] font-semibold tracking-[0.15em] text-white transition-colors hover:bg-[var(--navy-2)]"
                  >
                    VIEW RUN {runId ?? ""}
                    <span>→</span>
                  </button>

                  <button
                    type="button"
                    onClick={resetRun}
                    className="border border-[var(--border-strong)] bg-[var(--surface)] px-5 py-4 font-mono text-[9px] font-semibold tracking-[0.14em] text-[var(--ink-soft)] transition-colors hover:border-[var(--ink)]"
                  >
                    RESET
                  </button>
                </>
              )}
            </div>

            {!canRun &&
              !completed &&
              runMode === "custom" &&
              !running && (
                <p className="mt-3 font-mono text-[8px] tracking-[0.08em] text-[var(--amber)]">
                  SELECT BOTH SOURCE FILES TO ENABLE RECONCILIATION.
                </p>
              )}
          </div>
        </div>

        {/* =====================================================
            ENGINE PIPELINE
            ===================================================== */}

        <div className="lg:sticky lg:top-[96px] lg:self-start">
          <PipelineStatus
            steps={pipeline}
            running={running}
            completed={completed}
          />
        </div>
      </div>

      {/* =====================================================
          FOOTER CONTEXT
          ===================================================== */}

      <div className="mt-8 grid gap-3 border-t border-[var(--border)] py-5 font-mono text-[8px] tracking-[0.08em] text-[var(--ink-muted)] sm:grid-cols-2">
        <span>
          {runMode === "demo"
            ? "DEMO MODE · SYNTHETIC BENCHMARK · NO LIVE FINANCIAL DATA"
            : "CUSTOM MODE · USER-PROVIDED SOURCE DATA"}
        </span>

        <span className="sm:text-right">
          SAFE AUTOMATION REQUIRES VERIFIED EVIDENCE
        </span>
      </div>
    </section>
  );
}

/* =============================================================
   MODE BUTTON
   ============================================================= */

function ModeButton({
  active,
  onClick,
  label,
  detail,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
  detail: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        "flex min-h-[78px] flex-1 items-center justify-between gap-5 border px-5 py-4 text-left transition-all",
        active
          ? "border-[var(--navy)] bg-[var(--navy)] text-white"
          : "border-transparent bg-transparent text-[var(--ink-soft)] hover:border-[var(--border)] hover:bg-[var(--surface-soft)]",
      ].join(" ")}
    >
      <span>
        <span className="block font-mono text-[10px] font-semibold tracking-[0.15em]">
          {label}
        </span>

        <span
          className={[
            "mt-1.5 block text-xs leading-5",
            active
              ? "text-[#AEBAC6]"
              : "text-[var(--ink-muted)]",
          ].join(" ")}
        >
          {detail}
        </span>
      </span>

      {active && (
        <span className="shrink-0 font-mono text-[8px] font-semibold tracking-[0.14em] text-[var(--copper)]">
          ACTIVE
        </span>
      )}
    </button>
  );
}

/* =============================================================
   PANEL HEADING
   ============================================================= */

function PanelHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div>
      <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--ink-muted)]">
        {eyebrow}
      </div>

      <h2 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-[var(--ink)]">
        {title}
      </h2>

      <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--ink-muted)]">
        {description}
      </p>
    </div>
  );
}

/* =============================================================
   CONFIG FIELD
   ============================================================= */

function ConfigField({
  label,
  value,
  onChange,
  suffix,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  suffix?: string;
}) {
  return (
    <label className="block">
      <span className="mb-2 block font-mono text-[8px] font-medium tracking-[0.14em] text-[var(--ink-muted)]">
        {label}
      </span>

      <span className="flex border border-[var(--border)] bg-[var(--surface-soft)] transition-colors focus-within:border-[var(--copper)] focus-within:bg-white">
        <input
          value={value}
          onChange={(event) => {
            onChange(event.target.value);
          }}
          inputMode="decimal"
          className="min-w-0 flex-1 bg-transparent px-3 py-3 font-mono text-sm text-[var(--ink)] outline-none"
        />

        {suffix && (
          <span className="flex items-center px-3 font-mono text-[8px] tracking-[0.1em] text-[var(--ink-muted)]">
            {suffix}
          </span>
        )}
      </span>
    </label>
  );
}

/* =============================================================
   CONTROL ROW
   ============================================================= */

function ControlRow({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "lime" | "blue" | "amber";
}) {
  const toneClass =
    tone === "lime"
      ? "text-[var(--lime)]"
      : tone === "blue"
        ? "text-[var(--blue)]"
        : "text-[var(--amber)]";

  return (
    <div className="flex items-center justify-between bg-[var(--surface-soft)] px-5 py-4">
      <span className="font-mono text-[8px] font-medium tracking-[0.12em] text-[var(--ink-muted)]">
        {label}
      </span>

      <span
        className={`font-mono text-[8px] font-semibold tracking-[0.12em] ${toneClass}`}
      >
        ● {value}
      </span>
    </div>
  );
}

/* =============================================================
   INFO CHIP
   ============================================================= */

function InfoChip({
  text,
}: {
  text: string;
}) {
  return (
    <span className="border border-[var(--copper)]/40 bg-white/60 px-2.5 py-1.5 font-mono text-[8px] font-semibold tracking-[0.12em] text-[var(--copper-dark)]">
      {text}
    </span>
  );
}

/* =============================================================
   DEMO METRIC
   ============================================================= */

function DemoMetric({
  value,
  label,
  tone,
}: {
  value: string;
  label: string;
  tone: "lime" | "amber" | "blue" | "copper";
}) {
  const valueClass =
    tone === "lime"
      ? "text-[var(--lime)]"
      : tone === "amber"
        ? "text-[#D7A45B]"
        : tone === "blue"
          ? "text-[#71B9D2]"
          : "text-[var(--copper)]";

  return (
    <div className="bg-[var(--navy)] p-4">
      <div
        className={`font-mono text-xl font-medium ${valueClass}`}
      >
        {value}
      </div>

      <div className="mt-1.5 font-mono text-[7px] tracking-[0.14em] text-[#8796A6]">
        {label}
      </div>
    </div>
  );
}