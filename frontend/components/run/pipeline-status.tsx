type PipelineStatusValue =
  | "pending"
  | "active"
  | "complete";

type PipelineStep = {
  label: string;
  description: string;
  status: PipelineStatusValue;
};

type PipelineStatusProps = {
  steps: PipelineStep[];
  running: boolean;
  completed: boolean;
};

export function PipelineStatus({
  steps,
  running,
  completed,
}: PipelineStatusProps) {
  const statusLabel = completed
    ? "RUN COMPLETE"
    : running
      ? "PROCESSING"
      : "READY";

  const statusTone = completed
    ? "lime"
    : running
      ? "blue"
      : "neutral";

  return (
    <div className="overflow-hidden border border-[var(--border-dark)] bg-[var(--navy)] text-white shadow-[var(--shadow-md)]">
      {/* Header */}

      <div className="flex items-center justify-between border-b border-[#35485F] px-5 py-5">
        <div>
          <div className="font-mono text-[8px] tracking-[0.2em] text-[#8E9DAD]">
            ENGINE PIPELINE
          </div>

          <div className="mt-1 text-xs text-[#B3BEC9]">
            Decision lifecycle
          </div>
        </div>

        <PipelineStatusBadge tone={statusTone}>
          {statusLabel}
        </PipelineStatusBadge>
      </div>

      {/* Steps */}

      <div className="divide-y divide-[#2B3C50]">
        {steps.map((step, index) => (
          <div
            key={step.label}
            className={[
              "relative px-5 py-5 transition-colors",
              step.status === "active"
                ? "bg-[var(--navy-2)]"
                : "",
            ].join(" ")}
          >
            {step.status === "active" && (
              <div className="absolute left-0 top-0 h-full w-1 bg-[var(--blue)]" />
            )}

            {step.status === "complete" && (
              <div className="absolute left-0 top-0 h-full w-1 bg-[var(--lime)]" />
            )}

            <div className="flex items-start gap-4">
              <div className="flex h-7 w-7 shrink-0 items-center justify-center border border-[#425469] font-mono text-[8px] text-[#8D9BAB]">
                {String(index + 1).padStart(2, "0")}
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-3">
                  <span
                    className={[
                      "font-mono text-[9px] font-semibold tracking-[0.13em]",
                      step.status === "active"
                        ? "text-[#79C0D7]"
                        : step.status === "complete"
                          ? "text-[#C0DC98]"
                          : "text-[#D0D8E0]",
                    ].join(" ")}
                  >
                    {step.label}
                  </span>

                  <StepIndicator status={step.status} />
                </div>

                <p className="mt-2 text-xs leading-5 text-[#78889A]">
                  {step.description}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}

      <div className="border-t border-[#35485F] px-5 py-5">
        <div className="flex items-center justify-between">
          <span className="font-mono text-[8px] tracking-[0.15em] text-[#6F8092]">
            AUTHORITY MODEL
          </span>

          <span className="font-mono text-[8px] font-semibold tracking-[0.13em] text-[var(--copper)]">
            EVIDENCE → POLICY
          </span>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-2">
          <MiniSignal
            label="RULES"
            value="FIRST"
            tone="neutral"
          />

          <MiniSignal
            label="AI"
            value="BOUNDED"
            tone="blue"
          />

          <MiniSignal
            label="REVIEW"
            value="EXPLICIT"
            tone="amber"
          />
        </div>
      </div>
    </div>
  );
}

function StepIndicator({
  status,
}: {
  status: PipelineStatusValue;
}) {
  if (status === "complete") {
    return (
      <span className="font-mono text-[8px] font-semibold tracking-[0.1em] text-[var(--lime)]">
        ✓ DONE
      </span>
    );
  }

  if (status === "active") {
    return (
      <span className="flex items-center gap-1.5 font-mono text-[8px] font-semibold tracking-[0.1em] text-[var(--blue)]">
        <span className="h-2 w-2 animate-pulse rounded-full bg-[var(--blue)]" />
        ACTIVE
      </span>
    );
  }

  return (
    <span className="font-mono text-[8px] tracking-[0.1em] text-[#596B7E]">
      WAIT
    </span>
  );
}

function PipelineStatusBadge({
  children,
  tone,
}: {
  children: string;
  tone: "neutral" | "blue" | "lime";
}) {
  const className =
    tone === "lime"
      ? "border-[var(--lime)] text-[var(--lime)]"
      : tone === "blue"
        ? "border-[var(--blue)] text-[#79C0D7]"
        : "border-[#4A5D72] text-[#91A1B1]";

  return (
    <span
      className={`border px-2.5 py-1.5 font-mono text-[8px] font-semibold tracking-[0.12em] ${className}`}
    >
      {children}
    </span>
  );
}

function MiniSignal({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "neutral" | "blue" | "amber";
}) {
  const valueClass =
    tone === "blue"
      ? "text-[#79C0D7]"
      : tone === "amber"
        ? "text-[#D7A65C]"
        : "text-[#B2BECA]";

  return (
    <div className="border border-[#35485F] bg-[#15263A] px-3 py-3">
      <div className="font-mono text-[7px] tracking-[0.12em] text-[#697A8C]">
        {label}
      </div>

      <div
        className={`mt-1 font-mono text-[7px] font-semibold tracking-[0.1em] ${valueClass}`}
      >
        {value}
      </div>
    </div>
  );
}