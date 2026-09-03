"use client";

import { useState } from "react";
import Link from "next/link";

type TraceKey = "S014" | "S027" | "S041";
type Tone = "copper" | "steel" | "green" | "amber" | "red" | "graphite";

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

const failureModes: [string, string, string, Tone][] = [
  ["INPUT", "Malformed or invalid source", "REJECT INPUT", "red"],
  ["RETRIEVAL", "No viable candidate", "REVIEW / NO MATCH", "amber"],
  ["AI", "Provider or model failure", "FALLBACK / ESCALATE", "steel"],
  ["VERIFY", "Evidence conflict", "STOP AUTOMATION", "copper"],
  ["POLICY", "Unauthorized state", "STOP", "red"],
];

function toneText(tone: Tone): string {
  switch (tone) {
    case "copper":
      return "text-[#A85F3E]";
    case "steel":
      return "text-[#557889]";
    case "green":
      return "text-[#617454]";
    case "amber":
      return "text-[#A97832]";
    case "red":
      return "text-[#A44A3D]";
    default:
      return "text-[#3D4449]";
  }
}

function toneFill(tone: Tone): string {
  switch (tone) {
    case "copper":
      return "bg-[#B56A45]";
    case "steel":
      return "bg-[#557889]";
    case "green":
      return "bg-[#617454]";
    case "amber":
      return "bg-[#A97832]";
    case "red":
      return "bg-[#A44A3D]";
    default:
      return "bg-[#3D4449]";
  }
}

function toneBorder(tone: Tone): string {
  switch (tone) {
    case "copper":
      return "border-[#B56A45]";
    case "steel":
      return "border-[#557889]";
    case "green":
      return "border-[#617454]";
    case "amber":
      return "border-[#A97832]";
    case "red":
      return "border-[#A44A3D]";
    default:
      return "border-[#3D4449]";
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
          <Link
            href="/"
            className="font-mono text-[9px] font-semibold tracking-[0.18em] text-[#606B72] transition-colors hover:text-[#A85F3E]"
          >
            LEDGERSYNC / ENGINEERING
          </Link>

          <nav className="hidden items-center gap-5 overflow-x-auto md:flex">
            {[
              ["architecture", "ARCHITECTURE"],
              ["authority", "AUTHORITY"],
              ["trace", "TRACE"],
              ["reliability", "RELIABILITY"],
              ["observability", "OBSERVABILITY"],
              ["evidence", "EVIDENCE"],
              ["production", "PRODUCTION"],
            ].map(([href, label]) => (
              <a
                key={href}
                href={`#${href}`}
                className="font-mono text-[8px] tracking-[0.12em] text-[#68737A] transition-colors hover:text-[#A85F3E]"
              >
                {label}
              </a>
            ))}
          </nav>

          <span className="font-mono text-[8px] font-semibold tracking-[0.12em] text-[#617454]">
            ● HEALTHY
          </span>
        </div>
      </div>

      {/* =====================================================
          HERO
          ===================================================== */}

      <header className="relative overflow-hidden border-b border-[#C9C4B8] py-14 sm:py-20 lg:py-24">
        <div className="absolute right-[-90px] top-0 hidden h-[300px] w-[300px] rounded-full border border-[#D8D3C9] lg:block" />
        <div className="absolute right-[35px] top-[72px] hidden h-[170px] w-[170px] rounded-full border border-[#E1DDD4] lg:block" />

        <div className="relative grid gap-12 lg:grid-cols-[1fr_390px] lg:items-end">
          <div>
            <div className="flex items-center gap-3">
              <span className="font-mono text-[9px] font-semibold tracking-[0.2em] text-[#B56A45]">
                05
              </span>

              <span className="h-px w-9 bg-[#B56A45]" />

              <span className="font-mono text-[10px] font-semibold tracking-[0.2em] text-[#66737D]">
                ENGINEERING REVIEW
              </span>
            </div>

            <h1 className="mt-7 max-w-6xl text-[clamp(3.4rem,8vw,7.8rem)] font-semibold leading-[0.84] tracking-[-0.078em]">
              Where AI
              <br />
              reasons.
              <br />
              Systems decide.
            </h1>

            <p className="mt-8 max-w-3xl text-base leading-7 text-[#626D73] sm:text-lg sm:leading-8">
              LedgerSync separates semantic reasoning from financial authority.
              Deterministic evidence, verification, and policy remain in control
              of the final outcome.
            </p>

            <div className="mt-7 flex flex-wrap items-center gap-x-5 gap-y-3">
              <span className="font-mono text-[10px] font-semibold tracking-[0.11em] text-[#A85F3E]">
                AI MAY PROPOSE
              </span>

              <span className="text-[#A0A4A1]">/</span>

              <span className="font-mono text-[10px] font-semibold tracking-[0.11em] text-[#617454]">
                EVIDENCE MUST AUTHORIZE
              </span>
            </div>
          </div>

          <div className="border-l border-[#C9C4B8] pl-7">
            <div className="font-mono text-[10px] font-semibold tracking-[0.16em] text-[#66737D]">
              VERIFIED SIGNAL
            </div>

            <div className="mt-6 grid grid-cols-3 gap-6">
              <SignalStat
                value="161"
                label="TESTS"
                tone="copper"
              />

              <SignalStat
                value="400"
                label="RECORDS"
                tone="steel"
              />

              <SignalStat
                value="0"
                label="FAILURES"
                tone="green"
              />
            </div>

            <div className="mt-8 border-t border-[#C9C4B8] pt-5">
              <div className="font-mono text-[9px] leading-6 tracking-[0.04em] text-[#737E84]">
                DOCKER · STRUCTURED LOGGING
                <br />
                PROMETHEUS · GRAFANA · OLLAMA
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* =====================================================
          ARCHITECTURE
          ===================================================== */}

      <section
        id="architecture"
        className="scroll-mt-20 pt-16"
      >
        <SectionHeader
          eyebrow="01 / SYSTEM ARCHITECTURE"
          title="A decision pipeline with an explicit AI boundary."
          description="The model is a capability inside the workflow, not the authority above it."
        />

        <div className="mt-10 overflow-x-auto pb-5">
          <div className="min-w-[1080px]">
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
                tone="steel"
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

            <div className="ml-[39%] mt-5 flex max-w-[510px] items-start gap-4">
              <div className="ml-3 h-12 w-px bg-[#557889]" />

              <div className="pt-10">
                <div className="font-mono text-[9px] font-semibold tracking-[0.15em] text-[#557889]">
                  CONDITIONAL AI PATH
                </div>

                <div className="mt-2 text-base font-semibold">
                  OLLAMA / QWEN 2.5 3B
                </div>

                <p className="mt-2 text-sm leading-6 text-[#69737A]">
                  Invoked only when deterministic evidence is insufficient,
                  then returned to verification before policy.
                </p>
              </div>
            </div>

            <div className="mt-10 flex flex-wrap items-center gap-4 border-y border-[#C9C4B8] py-6">
              <span className="font-mono text-[9px] font-semibold tracking-[0.15em] text-[#66737D]">
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

              <span className="ml-auto font-mono text-[9px] tracking-[0.1em] text-[#4E575C]">
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
        className="scroll-mt-20 pt-16"
      >
        <SectionHeader
          eyebrow="02 / AUTHORITY"
          title="Responsibility is explicit."
          description="The architecture prevents one uncertain component from silently becoming the final decision-maker."
        />

        <div className="mt-8 overflow-x-auto">
          <table className="w-full min-w-[950px] border-collapse">
            <thead>
              <tr className="border-b-2 border-[#25292D]">
                <th className="py-5 pr-8 text-left font-mono text-[9px] font-semibold tracking-[0.15em] text-[#66737D]">
                  COMPONENT
                </th>

                <th className="py-5 pr-8 text-left font-mono text-[9px] font-semibold tracking-[0.15em] text-[#66737D]">
                  ALLOWED
                </th>

                <th className="py-5 text-left font-mono text-[9px] font-semibold tracking-[0.15em] text-[#66737D]">
                  FORBIDDEN
                </th>
              </tr>
            </thead>

            <tbody>
              {authorityRows.map(
                ([component, allowed, forbidden], index) => (
                  <tr
                    key={component}
                    className="border-b border-[#D4CFC5] transition-colors hover:bg-[#EEEAE1]"
                  >
                    <td className="py-6 pr-8">
                      <div className="flex items-center gap-3">
                        <span
                          className={[
                            "h-2.5 w-2.5 rounded-full",
                            index === 0
                              ? "bg-[#B56A45]"
                              : index === 1
                                ? "bg-[#557889]"
                                : index === 2
                                  ? "bg-[#617454]"
                                  : "bg-[#3D4449]",
                          ].join(" ")}
                        />

                        <span className="font-mono text-[10px] font-semibold tracking-[0.08em]">
                          {component}
                        </span>
                      </div>
                    </td>

                    <td className="py-6 pr-8 text-base leading-7 text-[#59636A]">
                      {allowed}
                    </td>

                    <td className="py-6 text-base leading-7 text-[#9A5045]">
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
          description="Inspect the decision path rather than trusting a static architecture diagram."
        />

        <div className="mt-8 overflow-hidden bg-[#25292D] text-[#F3F0E8] shadow-[0_20px_70px_rgba(37,41,45,0.14)]">
          <div className="flex flex-col gap-5 border-b border-[#464B4F] px-7 py-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="font-mono text-[9px] font-semibold tracking-[0.18em] text-[#87939B]">
                TRACE REPLAY
              </div>

              <div className="mt-2 text-sm text-[#AEB6BA]">
                Select a representative control path.
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              {traces.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedTrace(item.id)}
                  className={[
                    "px-4 py-3 font-mono text-[9px] font-semibold tracking-[0.12em] transition-colors",
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

          <div className="grid lg:grid-cols-[300px_1fr]">
            <div className="border-b border-[#464B4F] p-7 lg:border-b-0 lg:border-r">
              <div className="font-mono text-[9px] tracking-[0.16em] text-[#7F8B93]">
                RECORD
              </div>

              <div className="mt-3 font-mono text-5xl font-semibold tracking-[-0.05em]">
                {trace.id}
              </div>

              <div className="mt-2 font-mono text-[9px] font-semibold tracking-[0.14em] text-[#D08A61]">
                {trace.scenario}
              </div>

              <div className="mt-9 space-y-6 border-t border-[#464B4F] pt-6">
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

            <div className="relative p-7 sm:p-9">
              <div className="absolute bottom-10 left-[12px] top-10 w-px bg-[#4A4F53]" />

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
                <span className="grid h-7 w-7 place-items-center rounded-full bg-[#A97832] font-mono text-[10px] font-semibold text-white">
                  !
                </span>

                <div>
                  <div className="font-mono text-[9px] tracking-[0.14em] text-[#D3A15E]">
                    FINAL CONTROL STATE
                  </div>

                  <div className="mt-1 text-xl font-semibold">
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
          title="Failure is part of the state model."
          description="The system is designed to stop, reject or escalate instead of forcing uncertain records into automation."
        />

        <div className="mt-9 grid gap-8 md:grid-cols-5">
          {failureModes.map(
            ([component, failure, response, tone]) => (
              <div
                key={component}
                className="border-t-2 border-transparent pt-5 transition-colors hover:border-[#B56A45]"
              >
                <div
                  className={`h-1.5 w-10 ${toneFill(tone)}`}
                />

                <div className="mt-5 font-mono text-[9px] font-semibold tracking-[0.14em] text-[#66737D]">
                  {component}
                </div>

                <div className="mt-3 text-base font-semibold leading-6">
                  {failure}
                </div>

                <div
                  className={`mt-5 font-mono text-[9px] font-semibold tracking-[0.12em] ${toneText(tone)}`}
                >
                  {response}
                </div>
              </div>
            ),
          )}
        </div>

        <div className="mt-10 grid gap-7 border-y border-[#C9C4B8] py-8 sm:grid-cols-3">
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
          description="Metrics and monitoring make the reconciliation engine inspectable beyond a successful run."
        />

        <div className="mt-9 grid gap-12 lg:grid-cols-[1fr_340px]">
          <div>
            <TelemetryRow
              label="reconciliation records"
              value="400"
              width="76%"
              tone="steel"
            />

            <TelemetryRow
              label="LLM invocations"
              value="90"
              width="22.5%"
              tone="steel"
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

            <div className="mt-10 border-t border-[#C9C4B8] pt-8">
              <div className="font-mono text-[9px] font-semibold tracking-[0.16em] text-[#66737D]">
                LATENCY DISTRIBUTION
              </div>

              <div className="mt-6 grid gap-7 sm:grid-cols-2">
                <Latency
                  label="P50"
                  value="78.01 ms"
                  tone="steel"
                />

                <Latency
                  label="P95"
                  value="11.51 s"
                  tone="copper"
                />
              </div>
            </div>
          </div>

          <div className="border-l border-[#C9C4B8] pl-8">
            <div className="font-mono text-[9px] font-semibold tracking-[0.16em] text-[#66737D]">
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
              tone="steel"
            />

            <MonitorConnector />

            <Monitor
              label="GRAFANA"
              status="VISUALIZED"
              tone="copper"
            />

            <div className="mt-8 border-t border-[#C9C4B8] pt-6">
              <div className="font-mono text-[8px] tracking-[0.12em] text-[#737E84]">
                TARGET
              </div>

              <div className="mt-2 font-mono text-base font-semibold">
                ledgersync
              </div>

              <div className="mt-1 font-mono text-[8px] text-[#7A848A]">
                scrape interval · 5s
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          ENGINEERING SURFACE
          ===================================================== */}

      <section className="pt-16">
        <SectionHeader
          eyebrow="06 / ENGINEERING SURFACE"
          title="The product is only the visible edge."
          description="The system behind the interface has its own engineering surface."
        />

        <div className="mt-9 grid gap-8 lg:grid-cols-[240px_1fr]">
          <div>
            <div className="font-mono text-[9px] font-semibold tracking-[0.16em] text-[#66737D]">
              VERIFIED TEST SURFACE
            </div>

            <div className="mt-2 font-mono text-7xl font-semibold tracking-[-0.07em]">
              161
            </div>

            <div className="mt-1 font-mono text-[9px] font-semibold tracking-[0.15em] text-[#B56A45]">
              TESTS PASSED
            </div>
          </div>

          <div className="grid gap-0 border-l border-[#C9C4B8] pl-8 sm:grid-cols-2">
            <SurfaceSignal
              title="TESTING"
              value="161 passed"
              detail="Current repository-level test result."
            />

            <SurfaceSignal
              title="RUNTIME"
              value="Docker"
              detail="Reproducible containerized environment."
            />

            <SurfaceSignal
              title="OBSERVABILITY"
              value="Prometheus + Grafana"
              detail="Runtime metrics and operational dashboards."
            />

            <SurfaceSignal
              title="AI CONTROL"
              value="Bounded"
              detail="Ollama is invoked selectively and does not authorize outcomes."
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
          description="A serious evaluation separates measured evidence from claims that still require production validation."
        />

        <div className="mt-9 grid border-y border-[#25292D] lg:grid-cols-2">
          <div className="py-10 lg:pr-10">
            <div className="font-mono text-[9px] font-semibold tracking-[0.18em] text-[#617454]">
              MEASURED · CURRENT HYBRID RUN
            </div>

            <div className="mt-7 space-y-5">
              <Proof
                label="Records evaluated"
                value="400"
              />

              <Proof
                label="Successful requests"
                value="400"
              />

              <Proof
                label="Resolution accuracy"
                value="76.00%"
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

          <div className="border-t border-[#C9C4B8] py-10 lg:border-l lg:border-t-0 lg:pl-10">
            <div className="font-mono text-[9px] font-semibold tracking-[0.18em] text-[#A97832]">
              NOT YET PROVEN
            </div>

            <div className="mt-7 space-y-5">
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
          PRODUCTION
          ===================================================== */}

      <section
        id="production"
        className="scroll-mt-20 pt-16"
      >
        <SectionHeader
          eyebrow="08 / PRODUCTION PATH"
          title="From benchmark to production."
          description="The remaining engineering work is visible and intentional."
        />

        <div className="mt-9 overflow-x-auto">
          <div className="min-w-[900px]">
            <div className="grid grid-cols-3 border-b-2 border-[#25292D] pb-4">
              <div className="font-mono text-[9px] font-semibold tracking-[0.16em] text-[#617454]">
                TODAY
              </div>

              <div className="font-mono text-[9px] font-semibold tracking-[0.16em] text-[#557889]">
                NEXT
              </div>

              <div className="font-mono text-[9px] font-semibold tracking-[0.16em] text-[#A97832]">
                PRODUCTION
              </div>
            </div>

            <ProductionRow
              today="Synthetic scenario data"
              next="Real transaction corpus"
              production="Live bank / PSP integrations"
            />

            <ProductionRow
              today="161 tests"
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
        <div className="border-t-2 border-[#25292D] pt-11">
          <div className="grid gap-12 lg:grid-cols-[1fr_380px]">
            <div>
              <div className="flex items-center gap-3">
                <span className="h-1 w-8 bg-[#B56A45]" />

                <span className="font-mono text-[9px] font-semibold tracking-[0.18em] text-[#66737D]">
                  ENGINEERING STANCE
                </span>
              </div>

              <h2 className="mt-6 max-w-5xl text-4xl font-semibold leading-[0.92] tracking-[-0.055em] sm:text-5xl lg:text-6xl">
                Intelligence can improve
                <br />
                without gaining authority.
              </h2>

              <p className="mt-7 max-w-3xl text-base leading-7 text-[#657077] sm:text-lg sm:leading-8">
                LedgerSync keeps reasoning, evidence, verification, and policy
                separate so a stronger model does not silently become a more
                powerful financial decision-maker.
              </p>
            </div>

            <div className="border-l border-[#C9C4B8] pl-8">
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
            <span className="font-mono text-[9px] font-semibold tracking-[0.16em] text-[#66737D]">
              LEDGERSYNC · ENGINEERING REVIEW
            </span>

            <div className="flex flex-wrap gap-2">
              <Link
                href="/evaluation"
                className="border border-[#A85F3E] px-5 py-3 font-mono text-[9px] font-semibold tracking-[0.13em] text-[#A85F3E] transition-colors hover:bg-[#A85F3E] hover:text-white"
              >
                VIEW EVALUATION
              </Link>

              <Link
                href="/exceptions"
                className="bg-[#25292D] px-5 py-3 font-mono text-[9px] font-semibold tracking-[0.13em] text-[#F3F0E8] transition-colors hover:bg-[#B56A45]"
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
      <div className="font-mono text-[10px] font-semibold tracking-[0.19em] text-[#B56A45]">
        {eyebrow}
      </div>

      <h2 className="mt-3 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
        {title}
      </h2>

      <p className="mt-4 max-w-3xl text-base leading-7 text-[#69737A]">
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
  tone: Tone;
}) {
  return (
    <div>
      <div
        className={`font-mono text-2xl font-semibold tracking-[-0.04em] ${toneText(tone)}`}
      >
        {value}
      </div>

      <div className="mt-1.5 font-mono text-[8px] font-semibold tracking-[0.13em] text-[#7A848A]">
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
  tone: Tone;
}) {
  return (
    <div className="w-[165px] border-l-2 border-[#3D4449] pl-4">
      <div className="font-mono text-[9px] text-[#7A848A]">
        {number}
      </div>

      <div className="mt-3 font-mono text-[11px] font-semibold tracking-[0.14em]">
        {title}
      </div>

      <div
        className={`mt-1.5 font-mono text-[8px] tracking-[0.1em] ${toneText(tone)}`}
      >
        {detail}
      </div>
    </div>
  );
}

function ArchitectureConnector() {
  return (
    <div className="flex min-w-[75px] flex-1 items-center px-3">
      <div className="h-px w-full bg-[#A7AAA5]" />

      <span className="font-mono text-[10px] text-[#9B9F9D]">
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
  tone: Tone;
}) {
  return (
    <span
      className={`border px-3.5 py-2 font-mono text-[9px] font-semibold tracking-[0.11em] ${toneBorder(tone)} ${toneText(tone)}`}
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
      <div className="font-mono text-[8px] font-semibold tracking-[0.13em] text-[#74818A]">
        {label}
      </div>

      <div className="mt-2 font-mono text-[11px] font-semibold text-[#E2E6E8]">
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
  tone: Tone;
  description?: string;
  items?: string[];
}) {
  return (
    <div className="relative flex gap-5 pb-9">
      <div
        className={[
          "relative z-10 grid h-7 w-7 shrink-0 place-items-center rounded-full border bg-[#25292D] font-mono text-[8px] font-semibold",
          toneBorder(tone),
          toneText(tone),
        ].join(" ")}
      >
        {number}
      </div>

      <div className="min-w-0">
        <div
          className={`font-mono text-[9px] font-semibold tracking-[0.15em] ${toneText(tone)}`}
        >
          {title}
        </div>

        {description && (
          <p className="mt-2 max-w-3xl text-base leading-7 text-[#B8C0C4]">
            {description}
          </p>
        )}

        {items && (
          <div className="mt-4 space-y-2">
            {items.map((item) => (
              <div
                key={item}
                className="font-mono text-[9px] leading-5 text-[#AAB3B8]"
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
    <div className="flex items-center gap-4">
      <span className="font-mono text-[9px] font-semibold tracking-[0.13em]">
        {title}
      </span>

      <span className="font-mono text-xl text-[#B56A45]">
        {symbol}
      </span>

      <span className="font-mono text-[9px] font-semibold tracking-[0.13em] text-[#66737D]">
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
  tone: Tone;
}) {
  return (
    <div className="mb-7">
      <div className="mb-2.5 flex items-center justify-between">
        <span className="font-mono text-[10px] tracking-[0.11em] text-[#66737D]">
          {label}
        </span>

        <span
          className={`font-mono text-[11px] font-semibold ${toneText(tone)}`}
        >
          {value}
        </span>
      </div>

      <div className="h-1.5 bg-[#DDD9CF]">
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
  tone: Tone;
}) {
  return (
    <div className="border-l-2 border-[#C9C4B8] pl-5">
      <div className="font-mono text-[9px] font-semibold tracking-[0.13em] text-[#66737D]">
        {label}
      </div>

      <div
        className={`mt-2 font-mono text-3xl font-semibold tracking-[-0.04em] ${toneText(tone)}`}
      >
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
  tone: Tone;
}) {
  return (
    <div className="flex items-center justify-between border-b border-[#D4CFC5] py-5">
      <span className="font-mono text-[9px] font-semibold tracking-[0.13em]">
        {label}
      </span>

      <span
        className={`font-mono text-[8px] font-semibold tracking-[0.11em] ${toneText(tone)}`}
      >
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
      <div className="font-mono text-[9px] font-semibold tracking-[0.14em] text-[#66737D]">
        {title}
      </div>

      <div className="mt-2 font-mono text-xl font-semibold text-[#557889]">
        {value}
      </div>

      <p className="mt-2 text-sm leading-6 text-[#768086]">
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
    <div className="flex items-center justify-between gap-6 border-b border-[#DDD8CE] pb-3.5">
      <span className="text-base text-[#626D73]">
        {label}
      </span>

      <span className="font-mono text-[11px] font-semibold text-[#25292D]">
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
    <div className="flex items-center gap-3 border-b border-[#DDD8CE] pb-3.5">
      <span className="font-mono text-[10px] text-[#A97832]">
        —
      </span>

      <span className="text-base text-[#70797E]">
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
      <div className="py-6 pr-8 text-base text-[#4F5A61]">
        {today}
      </div>

      <div className="border-l border-[#D4CFC5] px-8 py-6 text-base text-[#55717E]">
        {next}
      </div>

      <div className="border-l border-[#D4CFC5] py-6 pl-8 text-base text-[#8D6E36]">
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
        <span className="font-mono text-[8px] text-[#B56A45]">
          {number}
        </span>

        <span className="font-mono text-[9px] font-semibold tracking-[0.14em]">
          {title}
        </span>
      </div>

      <div className="mt-2 text-base text-[#68737A]">
        {text}
      </div>
    </div>
  );
}