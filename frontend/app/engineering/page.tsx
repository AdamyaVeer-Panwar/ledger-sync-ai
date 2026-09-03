"use client";

import { useState } from "react";
import Link from "next/link";

type TraceKey = "S014" | "S027" | "S041";

type Trace = {
  id: TraceKey;
  scenario: string;
  amount: string;
  merchant: string;
  reference: string;
  retrieval: string;
  rules: string[];
  ai: string;
  verifier: string;
  policy: string;
};

const traces: Trace[] = [
  {
    id: "S014",
    scenario: "MULTIPLE CANDIDATES",
    amount: "INR 12,450.00",
    merchant: "MERCHANT_042",
    reference: "PAY-84921",
    retrieval: "2 plausible ledger candidates returned.",
    rules: [
      "Merchant matched",
      "Currency matched",
      "Amount within tolerance",
      "Reference ambiguous",
    ],
    ai: "AI interpreted the ambiguous candidate context.",
    verifier:
      "Two plausible candidates remained. Evidence was insufficient for automatic authorization.",
    policy: "AUTO_MATCH rejected → HUMAN_REVIEW",
  },
  {
    id: "S027",
    scenario: "WRONG MERCHANT",
    amount: "INR 8,920.00",
    merchant: "MERCHANT_117",
    reference: "PAY-98134",
    retrieval: "1 candidate returned.",
    rules: [
      "Amount within tolerance",
      "Currency matched",
      "Reference found",
      "Merchant identity mismatch",
    ],
    ai: "AI fallback was not required.",
    verifier:
      "Candidate failed the merchant consistency requirement.",
    policy: "AUTO_MATCH rejected → HUMAN_REVIEW",
  },
  {
    id: "S041",
    scenario: "MISSING REFERENCE",
    amount: "INR 2,180.00",
    merchant: "MERCHANT_031",
    reference: "—",
    retrieval: "No reliable candidate reference.",
    rules: [
      "Merchant matched",
      "Amount within tolerance",
      "Reference unavailable",
      "Date within window",
    ],
    ai: "AI fallback was not required.",
    verifier:
      "No sufficiently identifying reference was available.",
    policy: "AUTO_MATCH rejected → HUMAN_REVIEW",
  },
];

const authorityRows = [
  ["RULE ENGINE", "Prove deterministic facts", "Infer unsupported meaning"],
  ["LLM RESOLVER", "Propose interpretation", "Authorize financial action"],
  ["VERIFIER", "Validate proposal against evidence", "Invent evidence"],
  ["POLICY", "Choose allowed outcome", "Override missing evidence"],
  ["PERSISTENCE", "Record outcome and state", "Create an unverified decision"],
];

const failureModes = [
  ["INPUT", "Malformed or invalid source", "REJECT INPUT", "red"],
  ["RETRIEVAL", "No viable candidate", "REVIEW / NO MATCH", "amber"],
  ["AI", "Provider or model failure", "FALLBACK / ESCALATE", "blue"],
  ["VERIFY", "Evidence conflict", "STOP AUTOMATION", "copper"],
  ["POLICY", "Unauthorized state", "STOP", "red"],
];

function toneText(tone: string): string {
  switch (tone) {
    case "copper":
      return "text-[#A85F3E]";
    case "blue":
      return "text-[#557889]";
    case "green":
      return "text-[#617454]";
    case "amber":
      return "text-[#A97832]";
    default:
      return "text-[#A44A3D]";
  }
}

function toneFill(tone: string): string {
  switch (tone) {
    case "copper":
      return "bg-[#B56A45]";
    case "blue":
      return "bg-[#557889]";
    case "green":
      return "bg-[#617454]";
    case "amber":
      return "bg-[#A97832]";
    default:
      return "bg-[#A44A3D]";
  }
}

export default function EngineeringPage() {
  const [selectedTrace, setSelectedTrace] =
    useState<TraceKey>("S014");

  const trace =
    traces.find((item) => item.id === selectedTrace) ??
    traces[0];

  return (
    <main className="mx-auto max-w-[1500px] text-[#25292D]">
      {/* =====================================================
          ENGINEERING NAV
          ===================================================== */}

      <div className="sticky top-0 z-30 -mx-4 border-b border-[#D3CEC4] bg-[#F3F0E8]/95 px-4 py-3 backdrop-blur sm:-mx-6 sm:px-6">
        <div className="flex items-center justify-between gap-4">
          <span className="font-mono text-[8px] font-semibold tracking-[0.18em] text-[#606B72]">
            LEDGERSYNC / ENGINEERING
          </span>

          <nav className="hidden items-center gap-5 overflow-x-auto md:flex">
            <a
              href="#architecture"
              className="font-mono text-[7px] tracking-[0.11em] text-[#68737A] hover:text-[#A85F3E]"
            >
              ARCHITECTURE
            </a>

            <a
              href="#authority"
              className="font-mono text-[7px] tracking-[0.11em] text-[#68737A] hover:text-[#A85F3E]"
            >
              AUTHORITY
            </a>

            <a
              href="#trace"
              className="font-mono text-[7px] tracking-[0.11em] text-[#68737A] hover:text-[#A85F3E]"
            >
              TRACE
            </a>

            <a
              href="#reliability"
              className="font-mono text-[7px] tracking-[0.11em] text-[#68737A] hover:text-[#A85F3E]"
            >
              RELIABILITY
            </a>

            <a
              href="#observability"
              className="font-mono text-[7px] tracking-[0.11em] text-[#68737A] hover:text-[#A85F3E]"
            >
              OBSERVABILITY
            </a>

            <a
              href="#evidence"
              className="font-mono text-[7px] tracking-[0.11em] text-[#68737A] hover:text-[#A85F3E]"
            >
              EVIDENCE
            </a>
          </nav>

          <span className="font-mono text-[7px] font-semibold tracking-[0.12em] text-[#617454]">
            ● HEALTHY
          </span>
        </div>
      </div>

      {/* =====================================================
          HERO
          ===================================================== */}

      <header className="relative border-b border-[#C9C4B8] py-14 sm:py-18 lg:py-24">
        <div className="absolute right-[-70px] top-8 hidden h-[260px] w-[260px] rounded-full border border-[#D8D3C9] lg:block" />
        <div className="absolute right-[-15px] top-[63px] hidden h-[165px] w-[165px] rounded-full border border-[#E1DDD4] lg:block" />

        <div className="relative grid gap-12 lg:grid-cols-[1fr_360px] lg:items-end">
          <div>
            <div className="flex items-center gap-3">
              <span className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[#B56A45]">
                05
              </span>

              <span className="h-px w-8 bg-[#B56A45]" />

              <span className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[#66737D]">
                ENGINEERING REVIEW
              </span>
            </div>

            <h1 className="mt-7 max-w-5xl text-[clamp(3.2rem,8vw,7.5rem)] font-semibold leading-[0.84] tracking-[-0.075em]">
              Understand
              <br />
              the machine.
            </h1>

            <p className="mt-8 max-w-2xl text-base leading-7 text-[#626D73] sm:text-lg">
              LedgerSync is built around a deliberate boundary:
              <strong className="text-[#25292D]">
                {" "}AI may propose. Evidence must authorize.
              </strong>
            </p>
          </div>

          <div className="border-l border-[#C9C4B8] pl-7">
            <div className="font-mono text-[8px] font-semibold tracking-[0.16em] text-[#66737D]">
              SYSTEM SIGNAL
            </div>

            <div className="mt-6 grid grid-cols-3 gap-5">
              <SignalStat
                value="150+"
                label="TESTS"
                tone="copper"
              />

              <SignalStat
                value="400"
                label="RECORDS"
                tone="blue"
              />

              <SignalStat
                value="0"
                label="FAILURES"
                tone="green"
              />
            </div>

            <div className="mt-7 border-t border-[#C9C4B8] pt-5 font-mono text-[7px] leading-5 tracking-[0.04em] text-[#7A848A]">
              DOCKER · STRUCTURED LOGGING · PROMETHEUS · GRAFANA · BOUNDED AI
            </div>
          </div>
        </div>
      </header>

      {/* =====================================================
          ARCHITECTURE
          ===================================================== */}

      <section
        id="architecture"
        className="scroll-mt-20 pt-14"
      >
        <SectionHeader
          eyebrow="01 / SYSTEM ARCHITECTURE"
          title="A decision pipeline with an explicit AI boundary."
          description="The model sits inside the system. It does not sit above it."
        />

        <div className="mt-9 overflow-x-auto pb-3">
          <div className="min-w-[1050px]">
            <div className="flex items-center">
              <ArchitectureNode
                number="01"
                title="INGEST"
                detail="source records"
                tone="graphite"
              />

              <ArchitectureConnector />

              <ArchitectureNode
                number="02"
                title="RETRIEVE"
                detail="bounded candidates"
                tone="blue"
              />

              <ArchitectureConnector />

              <ArchitectureNode
                number="03"
                title="RULES"
                detail="deterministic evidence"
                tone="copper"
              />

              <ArchitectureConnector />

              <ArchitectureNode
                number="04"
                title="VERIFY"
                detail="evidence gate"
                tone="green"
              />

              <ArchitectureConnector />

              <ArchitectureNode
                number="05"
                title="POLICY"
                detail="authorized action"
                tone="graphite"
              />
            </div>

            <div className="ml-[40%] mt-3 flex max-w-[440px] items-start gap-4">
              <div className="ml-3 h-10 w-px bg-[#557889]" />

              <div className="pt-8">
                <div className="font-mono text-[8px] font-semibold tracking-[0.15em] text-[#557889]">
                  CONDITIONAL AI PATH
                </div>

                <div className="mt-2 text-sm font-semibold">
                  LLM RESOLVER
                </div>

                <p className="mt-1 text-xs leading-5 text-[#6F797F]">
                  Invoked only when deterministic evidence is insufficient,
                  then returned to verification.
                </p>
              </div>
            </div>

            <div className="mt-10 flex flex-wrap items-center gap-4 border-y border-[#C9C4B8] py-5">
              <span className="font-mono text-[8px] font-semibold tracking-[0.15em] text-[#66737D]">
                AUTHORIZED OUTCOMES
              </span>

              <OutcomeToken
                label="AUTO_MATCH"
                tone="green"
              />

              <OutcomeToken
                label="HUMAN_REVIEW"
                tone="amber"
              />

              <OutcomeToken
                label="NO_MATCH"
                tone="red"
              />

              <span className="ml-auto font-mono text-[7px] tracking-[0.1em] text-[#7A848A]">
                POLICY DECIDES
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          AUTHORITY
          ===================================================== */}

      <section
        id="authority"
        className="scroll-mt-20 pt-14"
      >
        <SectionHeader
          eyebrow="02 / AUTHORITY"
          title="Responsibility is explicit."
          description="Each component has a defined authority boundary."
        />

        <div className="mt-8 overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse">
            <thead>
              <tr className="border-b-2 border-[#25292D]">
                <th className="py-4 pr-8 text-left font-mono text-[8px] tracking-[0.15em] text-[#66737D]">
                  COMPONENT
                </th>

                <th className="py-4 pr-8 text-left font-mono text-[8px] tracking-[0.15em] text-[#66737D]">
                  ALLOWED
                </th>

                <th className="py-4 text-left font-mono text-[8px] tracking-[0.15em] text-[#66737D]">
                  FORBIDDEN
                </th>
              </tr>
            </thead>

            <tbody>
              {authorityRows.map(
                ([component, allowed, forbidden], index) => (
                  <tr
                    key={component}
                    className="border-b border-[#D4CFC5]"
                  >
                    <td className="py-5 pr-8">
                      <div className="flex items-center gap-3">
                        <span
                          className={[
                            "h-2 w-2 rounded-full",
                            index === 0
                              ? "bg-[#B56A45]"
                              : index === 1
                                ? "bg-[#557889]"
                                : index === 2
                                  ? "bg-[#617454]"
                                  : "bg-[#3D4449]",
                          ].join(" ")}
                        />

                        <span className="font-mono text-[9px] font-semibold tracking-[0.08em]">
                          {component}
                        </span>
                      </div>
                    </td>

                    <td className="py-5 pr-8 text-sm text-[#59636A]">
                      {allowed}
                    </td>

                    <td className="py-5 text-sm text-[#9A5045]">
                      {forbidden}
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* =====================================================
          DECISION TRACE
          ===================================================== */}

      <section
        id="trace"
        className="scroll-mt-20 pt-16"
      >
        <SectionHeader
          eyebrow="03 / DECISION TRACE"
          title="Watch one transaction move through the system."
          description="Inspect the decision path instead of reading a static architecture diagram."
        />

        <div className="mt-8 overflow-hidden bg-[#25292D] text-[#F3F0E8] shadow-[0_18px_60px_rgba(37,41,45,0.12)]">
          <div className="flex flex-col gap-4 border-b border-[#464B4F] px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="font-mono text-[8px] font-semibold tracking-[0.18em] text-[#87939B]">
                TRACE REPLAY
              </div>

              <div className="mt-1 text-xs text-[#AEB6BA]">
                Select a representative control path.
              </div>
            </div>

            <div className="flex gap-2">
              {traces.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedTrace(item.id)}
                  className={[
                    "px-4 py-2.5 font-mono text-[8px] font-semibold tracking-[0.12em] transition-colors",
                    selectedTrace === item.id
                      ? "bg-[#B56A45] text-white"
                      : "bg-[#343A3E] text-[#AAB3B8] hover:bg-[#41484D]",
                  ].join(" ")}
                >
                  {item.id}
                </button>
              ))}
            </div>
          </div>

          <div className="grid lg:grid-cols-[280px_1fr]">
            <div className="border-b border-[#464B4F] p-6 lg:border-b-0 lg:border-r">
              <div className="font-mono text-[8px] tracking-[0.16em] text-[#7F8B93]">
                RECORD
              </div>

              <div className="mt-3 font-mono text-4xl font-semibold tracking-[-0.045em]">
                {trace.id}
              </div>

              <div className="mt-2 font-mono text-[8px] font-semibold tracking-[0.14em] text-[#D08A61]">
                {trace.scenario}
              </div>

              <div className="mt-8 space-y-5 border-t border-[#464B4F] pt-6">
                <DarkMeta
                  label="AMOUNT"
                  value={trace.amount}
                />

                <DarkMeta
                  label="MERCHANT"
                  value={trace.merchant}
                />

                <DarkMeta
                  label="REFERENCE"
                  value={trace.reference}
                />
              </div>
            </div>

            <div className="relative p-6 sm:p-8">
              <div className="absolute bottom-8 left-[11px] top-8 w-px bg-[#4A4F53]" />

              <TraceEvent
                number="01"
                title="RETRIEVAL"
                tone="steel"
                description={trace.retrieval}
              />

              <TraceEvent
                number="02"
                title="RULE ENGINE"
                tone="copper"
                items={trace.rules}
              />

              <TraceEvent
                number="03"
                title="AI RESOLVER"
                tone="steel"
                description={trace.ai}
              />

              <TraceEvent
                number="04"
                title="VERIFIER"
                tone="green"
                description={trace.verifier}
              />

              <TraceEvent
                number="05"
                title="POLICY"
                tone="graphite"
                description={trace.policy}
              />

              <div className="relative mt-1 flex items-center gap-4">
                <span className="grid h-6 w-6 place-items-center rounded-full bg-[#A97832] font-mono text-[9px] font-semibold text-white">
                  !
                </span>

                <div>
                  <div className="font-mono text-[8px] tracking-[0.14em] text-[#D3A15E]">
                    FINAL CONTROL STATE
                  </div>

                  <div className="mt-1 text-lg font-semibold">
                    HUMAN_REVIEW
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          RELIABILITY
          ===================================================== */}

      <section
        id="reliability"
        className="scroll-mt-20 pt-16"
      >
        <SectionHeader
          eyebrow="04 / RELIABILITY"
          title="Failure is designed into the system."
          description="Every important failure domain has a deliberate response."
        />

        <div className="mt-8 grid gap-7 md:grid-cols-5">
          {failureModes.map(
            ([component, failure, response, tone]) => (
              <div key={component}>
                <div
                  className={`h-1 w-9 ${toneFill(tone)}`}
                />

                <div className="mt-5 font-mono text-[8px] font-semibold tracking-[0.14em] text-[#66737D]">
                  {component}
                </div>

                <div className="mt-3 text-sm font-semibold leading-5">
                  {failure}
                </div>

                <div
                  className={`mt-5 font-mono text-[8px] font-semibold tracking-[0.12em] ${toneText(tone)}`}
                >
                  {response}
                </div>
              </div>
            ),
          )}
        </div>

        <div className="mt-9 grid gap-6 border-y border-[#C9C4B8] py-7 sm:grid-cols-3">
          <Principle
            title="UNKNOWN"
            symbol="≠"
            value="SUCCESS"
          />

          <Principle
            title="AMBIGUITY"
            symbol="≠"
            value="FAILURE"
          />

          <Principle
            title="UNVERIFIED"
            symbol="≠"
            value="AUTHORIZED"
          />
        </div>
      </section>

      {/* =====================================================
          OBSERVABILITY
          ===================================================== */}

      <section
        id="observability"
        className="scroll-mt-20 pt-16"
      >
        <SectionHeader
          eyebrow="05 / OBSERVABILITY"
          title="A working system should be measurable."
          description="Operational signals expose what the benchmark is actually doing."
        />

        <div className="mt-8 grid gap-10 lg:grid-cols-[1fr_320px]">
          <div>
            <TelemetryRow
              label="reconciliation records"
              value="400"
              width="76%"
              tone="blue"
            />

            <TelemetryRow
              label="LLM invocations"
              value="90"
              width="22.5%"
              tone="blue"
            />

            <TelemetryRow
              label="failures"
              value="0"
              width="0%"
              tone="green"
            />

            <TelemetryRow
              label="auto-match precision"
              value="100.00%"
              width="100%"
              tone="green"
            />

            <div className="mt-10 border-t border-[#C9C4B8] pt-7">
              <div className="font-mono text-[8px] font-semibold tracking-[0.16em] text-[#66737D]">
                LATENCY DISTRIBUTION
              </div>

              <div className="mt-6 grid gap-6 sm:grid-cols-2">
                <Latency
                  label="P50"
                  value="78.01 ms"
                  tone="blue"
                />

                <Latency
                  label="P95"
                  value="11.51 s"
                  tone="copper"
                />
              </div>
            </div>
          </div>

          <div className="border-l border-[#C9C4B8] pl-7">
            <div className="font-mono text-[8px] font-semibold tracking-[0.16em] text-[#66737D]">
              MONITORING PATH
            </div>

            <Monitor
              label="APPLICATION"
              status="INSTRUMENTED"
              tone="green"
            />

            <MonitorConnector />

            <Monitor
              label="PROMETHEUS"
              status="SCRAPING"
              tone="blue"
            />

            <MonitorConnector />

            <Monitor
              label="GRAFANA"
              status="VISUALIZED"
              tone="copper"
            />

            <div className="mt-8 border-t border-[#C9C4B8] pt-5">
              <div className="font-mono text-[7px] tracking-[0.12em] text-[#737E84]">
                TARGET
              </div>

              <div className="mt-2 font-mono text-sm font-semibold">
                ledgersync
              </div>

              <div className="mt-1 font-mono text-[7px] text-[#7A848A]">
                scrape interval · 5s
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          ENGINEERING SIGNAL
          ===================================================== */}

      <section className="pt-16">
        <SectionHeader
          eyebrow="06 / ENGINEERING SURFACE"
          title="The product is only the visible edge."
          description="The underlying system is supported by testing, containerization, observability and explicit AI controls."
        />

        <div className="mt-9 grid gap-8 lg:grid-cols-[220px_1fr]">
          <div>
            <div className="font-mono text-[8px] font-semibold tracking-[0.16em] text-[#66737D]">
              CONFIDENCE SIGNAL
            </div>

            <div className="mt-3 font-mono text-7xl font-semibold tracking-[-0.07em]">
              150+
            </div>

            <div className="mt-1 font-mono text-[8px] font-semibold tracking-[0.15em] text-[#B56A45]">
              TESTS
            </div>
          </div>

          <div className="grid gap-0 border-l border-[#C9C4B8] pl-7 sm:grid-cols-2">
            <SurfaceSignal
              title="TESTING"
              value="150+ tests"
              detail="Project-level verification surface."
            />

            <SurfaceSignal
              title="RUNTIME"
              value="Docker"
              detail="Reproducible containerized environment."
            />

            <SurfaceSignal
              title="OBSERVABILITY"
              value="Prometheus + Grafana"
              detail="Operational metrics and dashboards."
            />

            <SurfaceSignal
              title="AI CONTROL"
              value="Bounded"
              detail="The model does not own final authorization."
            />
          </div>
        </div>
      </section>

      {/* =====================================================
          EVIDENCE
          ===================================================== */}

      <section
        id="evidence"
        className="scroll-mt-20 pt-16"
      >
        <SectionHeader
          eyebrow="07 / EVIDENCE BOUNDARY"
          title="Know what the benchmark proves."
          description="The strongest engineering claim is often knowing what not to claim."
        />

        <div className="mt-9 grid border-y border-[#25292D] lg:grid-cols-2">
          <div className="py-9 lg:pr-10">
            <div className="font-mono text-[8px] font-semibold tracking-[0.18em] text-[#617454]">
              MEASURED
            </div>

            <div className="mt-7 space-y-4">
              <Proof
                label="Records evaluated"
                value="400"
              />

              <Proof
                label="Successful requests"
                value="400"
              />

              <Proof
                label="Auto-match precision"
                value="100.00%"
              />

              <Proof
                label="Auto-match recall"
                value="89.41%"
              />

              <Proof
                label="False auto-match"
                value="0.00%"
              />

              <Proof
                label="LLM invocation rate"
                value="22.50%"
              />
            </div>
          </div>

          <div className="border-t border-[#C9C4B8] py-9 lg:border-l lg:border-t-0 lg:pl-10">
            <div className="font-mono text-[8px] font-semibold tracking-[0.18em] text-[#A97832]">
              NOT YET PROVEN
            </div>

            <div className="mt-7 space-y-4">
              <Unproven text="Production accuracy" />
              <Unproven text="Live bank integration behaviour" />
              <Unproven text="Production throughput" />
              <Unproven text="Real-data threshold calibration" />
              <Unproven text="Provider-level resilience" />
              <Unproven text="Long-term production SLOs" />
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          PRODUCTION PATH
          ===================================================== */}

      <section className="pt-16">
        <SectionHeader
          eyebrow="08 / PRODUCTION PATH"
          title="From benchmark to production."
          description="The remaining work is visible instead of being hidden behind a production-ready label."
        />

        <div className="mt-9 overflow-x-auto">
          <div className="min-w-[900px]">
            <div className="grid grid-cols-3 border-b-2 border-[#25292D] pb-4">
              <div className="font-mono text-[8px] font-semibold tracking-[0.16em] text-[#617454]">
                TODAY
              </div>

              <div className="font-mono text-[8px] font-semibold tracking-[0.16em] text-[#557889]">
                NEXT
              </div>

              <div className="font-mono text-[8px] font-semibold tracking-[0.16em] text-[#A97832]">
                PRODUCTION
              </div>
            </div>

            <ProductionRow
              today="Synthetic scenario data"
              next="Real transaction corpus"
              production="Live bank / PSP integrations"
            />

            <ProductionRow
              today="150+ tests"
              next="CI + automated regression"
              production="Continuous delivery gates"
            />

            <ProductionRow
              today="Prometheus + Grafana"
              next="SLOs + alerting"
              production="Operational ownership"
            />

            <ProductionRow
              today="Bounded AI path"
              next="Provider failover"
              production="Multi-provider resilience"
            />

            <ProductionRow
              today="Fixed benchmark thresholds"
              next="Threshold calibration"
              production="Data-driven policy tuning"
            />

            <ProductionRow
              today="Docker runtime"
              next="Load testing"
              production="Horizontal scaling"
            />
          </div>
        </div>
      </section>

      {/* =====================================================
          FINAL
          ===================================================== */}

      <section className="pb-8 pt-20">
        <div className="border-t-2 border-[#25292D] pt-10">
          <div className="grid gap-12 lg:grid-cols-[1fr_360px]">
            <div>
              <div className="flex items-center gap-3">
                <span className="h-1 w-8 bg-[#B56A45]" />

                <span className="font-mono text-[8px] font-semibold tracking-[0.18em] text-[#66737D]">
                  ENGINEERING STANCE
                </span>
              </div>

              <h2 className="mt-6 max-w-5xl text-4xl font-semibold leading-[0.92] tracking-[-0.055em] sm:text-5xl lg:text-6xl">
                AI is a component.
                <br />
                The system owns the decision.
              </h2>

              <p className="mt-7 max-w-3xl text-base leading-7 text-[#657077]">
                LedgerSync is deliberately structured so intelligence can
                improve independently from authorization. A stronger model
                should improve reasoning without silently gaining control over
                the final financial decision.
              </p>
            </div>

            <div className="border-l border-[#C9C4B8] pl-7">
              <Stance
                number="01"
                title="BUILD"
                text="Make the system work."
              />

              <Stance
                number="02"
                title="MEASURE"
                text="Prove what it actually does."
              />

              <Stance
                number="03"
                title="CONSTRAIN"
                text="Keep uncertain components bounded."
              />
            </div>
          </div>

          <div className="mt-12 flex flex-col gap-4 border-t border-[#C9C4B8] pt-6 sm:flex-row sm:items-center sm:justify-between">
            <span className="font-mono text-[8px] font-semibold tracking-[0.16em] text-[#66737D]">
              LEDGERSYNC · ENGINEERING REVIEW
            </span>

            <div className="flex flex-wrap gap-2">
              <Link
                href="/evaluation"
                className="border border-[#A85F3E] px-4 py-3 font-mono text-[8px] font-semibold tracking-[0.13em] text-[#A85F3E] transition-colors hover:bg-[#A85F3E] hover:text-white"
              >
                VIEW EVALUATION
              </Link>

              <Link
                href="/exceptions"
                className="bg-[#25292D] px-4 py-3 font-mono text-[8px] font-semibold tracking-[0.13em] text-[#F3F0E8] transition-colors hover:bg-[#B56A45]"
              >
                INSPECT EXCEPTIONS
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

/* =============================================================
   SUPPORTING COMPONENTS
   ============================================================= */

function SectionHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div className="max-w-4xl">
      <div className="font-mono text-[8px] font-semibold tracking-[0.19em] text-[#B56A45]">
        {eyebrow}
      </div>

      <h2 className="mt-3 text-2xl font-semibold tracking-[-0.035em] sm:text-3xl">
        {title}
      </h2>

      <p className="mt-3 max-w-3xl text-sm leading-6 text-[#69737A]">
        {description}
      </p>
    </div>
  );
}

function SignalStat({
  value,
  label,
  tone,
}: {
  value: string;
  label: string;
  tone: string;
}) {
  return (
    <div>
      <div className={`font-mono text-xl font-semibold ${toneText(tone)}`}>
        {value}
      </div>

      <div className="mt-1 font-mono text-[7px] font-semibold tracking-[0.13em] text-[#7A848A]">
        {label}
      </div>
    </div>
  );
}

function ArchitectureNode({
  number,
  title,
  detail,
  tone,
}: {
  number: string;
  title: string;
  detail: string;
  tone: string;
}) {
  return (
    <div className="w-[155px] border-l-2 border-[#3D4449] pl-4">
      <div className="font-mono text-[8px] text-[#7A848A]">
        {number}
      </div>

      <div className="mt-3 font-mono text-[10px] font-semibold tracking-[0.14em]">
        {title}
      </div>

      <div className={`mt-1 font-mono text-[7px] tracking-[0.1em] ${toneText(tone)}`}>
        {detail}
      </div>
    </div>
  );
}

function ArchitectureConnector() {
  return (
    <div className="flex min-w-[70px] flex-1 items-center px-3">
      <div className="h-px w-full bg-[#A7AAA5]" />
      <span className="font-mono text-[9px] text-[#9B9F9D]">
        →
      </span>
    </div>
  );
}

function OutcomeToken({
  label,
  tone,
}: {
  label: string;
  tone: string;
}) {
  const border =
    tone === "green"
      ? "border-[#617454]"
      : tone === "amber"
        ? "border-[#A97832]"
        : "border-[#A44A3D]";

  return (
    <span
      className={`border px-3 py-2 font-mono text-[8px] font-semibold tracking-[0.11em] ${border} ${toneText(tone)}`}
    >
      {label}
    </span>
  );
}

function DarkMeta({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div>
      <div className="font-mono text-[7px] tracking-[0.13em] text-[#74818A]">
        {label}
      </div>

      <div className="mt-1.5 font-mono text-[9px] font-semibold text-[#E2E6E8]">
        {value}
      </div>
    </div>
  );
}

function TraceEvent({
  number,
  title,
  tone,
  description,
  items,
}: {
  number: string;
  title: string;
  tone: string;
  description?: string;
  items?: string[];
}) {
  return (
    <div className="relative flex gap-5 pb-8">
      <div
        className={[
          "relative z-10 grid h-6 w-6 shrink-0 place-items-center rounded-full border bg-[#25292D] font-mono text-[7px] font-semibold",
          tone === "steel"
            ? "border-[#557889]"
            : tone === "copper"
              ? "border-[#B56A45]"
              : tone === "green"
                ? "border-[#617454]"
                : "border-[#6B7277]",
          toneText(tone),
        ].join(" ")}
      >
        {number}
      </div>

      <div>
        <div className={`font-mono text-[8px] font-semibold tracking-[0.15em] ${toneText(tone)}`}>
          {title}
        </div>

        {description && (
          <p className="mt-2 max-w-3xl text-sm leading-6 text-[#B8C0C4]">
            {description}
          </p>
        )}

        {items && (
          <div className="mt-3 space-y-1.5">
            {items.map((item) => (
              <div
                key={item}
                className="font-mono text-[8px] text-[#AAB3B8]"
              >
                <span className="mr-2 text-[#87A27A]">
                  ✓
                </span>
                {item}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function Principle({
  title,
  symbol,
  value,
}: {
  title: string;
  symbol: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-3">
      <span className="font-mono text-[8px] font-semibold tracking-[0.13em]">
        {title}
      </span>

      <span className="font-mono text-lg text-[#B56A45]">
        {symbol}
      </span>

      <span className="font-mono text-[8px] font-semibold tracking-[0.13em] text-[#66737D]">
        {value}
      </span>
    </div>
  );
}

function TelemetryRow({
  label,
  value,
  width,
  tone,
}: {
  label: string;
  value: string;
  width: string;
  tone: string;
}) {
  return (
    <div className="mb-6">
      <div className="mb-2 flex items-center justify-between">
        <span className="font-mono text-[8px] tracking-[0.11em] text-[#66737D]">
          {label}
        </span>

        <span className={`font-mono text-[9px] font-semibold ${toneText(tone)}`}>
          {value}
        </span>
      </div>

      <div className="h-1 bg-[#DDD9CF]">
        <div
          className={`h-full ${toneFill(tone)}`}
          style={{ width }}
        />
      </div>
    </div>
  );
}

function Latency({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: string;
}) {
  return (
    <div className="border-l-2 border-[#C9C4B8] pl-4">
      <div className="font-mono text-[8px] font-semibold tracking-[0.13em] text-[#66737D]">
        {label}
      </div>

      <div className={`mt-2 font-mono text-2xl font-semibold tracking-[-0.03em] ${toneText(tone)}`}>
        {value}
      </div>
    </div>
  );
}

function Monitor({
  label,
  status,
  tone,
}: {
  label: string;
  status: string;
  tone: string;
}) {
  return (
    <div className="flex items-center justify-between border-b border-[#D4CFC5] py-4">
      <span className="font-mono text-[8px] font-semibold tracking-[0.13em]">
        {label}
      </span>

      <span className={`font-mono text-[7px] font-semibold tracking-[0.11em] ${toneText(tone)}`}>
        ● {status}
      </span>
    </div>
  );
}

function MonitorConnector() {
  return (
    <div className="ml-2 h-5 border-l border-[#A9AAA6]" />
  );
}

function SurfaceSignal({
  title,
  value,
  detail,
}: {
  title: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="border-b border-[#D4CFC5] pb-7 pr-7 pt-1">
      <div className="font-mono text-[8px] font-semibold tracking-[0.14em] text-[#66737D]">
        {title}
      </div>

      <div className="mt-2 font-mono text-lg font-semibold text-[#557889]">
        {value}
      </div>

      <p className="mt-1.5 text-xs leading-5 text-[#768086]">
        {detail}
      </p>
    </div>
  );
}

function Proof({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between gap-5 border-b border-[#DDD8CE] pb-3">
      <span className="text-sm text-[#626D73]">
        {label}
      </span>

      <span className="font-mono text-[9px] font-semibold text-[#25292D]">
        {value}
      </span>
    </div>
  );
}

function Unproven({
  text,
}: {
  text: string;
}) {
  return (
    <div className="flex items-center gap-3 border-b border-[#DDD8CE] pb-3">
      <span className="font-mono text-[9px] text-[#A97832]">
        —
      </span>

      <span className="text-sm text-[#70797E]">
        {text}
      </span>
    </div>
  );
}

function ProductionRow({
  today,
  next,
  production,
}: {
  today: string;
  next: string;
  production: string;
}) {
  return (
    <div className="grid grid-cols-3 border-b border-[#D4CFC5]">
      <div className="py-5 pr-8 text-sm text-[#4F5A61]">
        {today}
      </div>

      <div className="border-l border-[#D4CFC5] px-8 py-5 text-sm text-[#55717E]">
        {next}
      </div>

      <div className="border-l border-[#D4CFC5] py-5 pl-8 text-sm text-[#8D6E36]">
        {production}
      </div>
    </div>
  );
}

function Stance({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (
    <div className="border-b border-[#D4CFC5] py-5 first:pt-0 last:border-b-0">
      <div className="flex items-center gap-3">
        <span className="font-mono text-[7px] text-[#B56A45]">
          {number}
        </span>

        <span className="font-mono text-[8px] font-semibold tracking-[0.14em]">
          {title}
        </span>
      </div>

      <div className="mt-2 text-sm text-[#68737A]">
        {text}
      </div>
    </div>
  );
}