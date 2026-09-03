"use client";

import { useMemo, useState } from "react";

type ExceptionType =
  | "MULTIPLE_CANDIDATES"
  | "WRONG_MERCHANT"
  | "MISSING_REFERENCE"
  | "DATE_LAG"
  | "PARTIAL_REFUND";

type EvidenceStatus =
  | "verified"
  | "conflict"
  | "missing";

type EvidenceItem = {
  label: string;
  status: EvidenceStatus;
  detail: string;
};

type ExceptionRecord = {
  id: string;
  reason: ExceptionType;
  confidence: string;
  candidates: string[];
  merchant: string;
  amount: string;
  currency: string;
  reference: string;
  settlementDate: string;
  aiInvoked: boolean;
  evidence: EvidenceItem[];
};

/* =============================================================
   23 REPRESENTATIVE CASES
   ============================================================= */

const exceptions: ExceptionRecord[] = [
  /* -----------------------------------------------------------
     MULTIPLE CANDIDATES — 6
     ----------------------------------------------------------- */

  {
    id: "S014",
    reason: "MULTIPLE_CANDIDATES",
    confidence: "0.71",
    candidates: ["L102", "L118"],
    merchant: "MERCHANT_042",
    amount: "12,450.00",
    currency: "INR",
    reference: "PAY-84921",
    settlementDate: "2026-08-14",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "CURRENCY",
        status: "verified",
        detail: "INR",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Within tolerance",
      },
      {
        label: "REFERENCE",
        status: "conflict",
        detail: "Two plausible ledger records",
      },
    ],
  },
  {
    id: "S018",
    reason: "MULTIPLE_CANDIDATES",
    confidence: "0.68",
    candidates: ["L126", "L133"],
    merchant: "MERCHANT_014",
    amount: "7,850.00",
    currency: "INR",
    reference: "PAY-93218",
    settlementDate: "2026-08-14",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Exact",
      },
      {
        label: "REFERENCE",
        status: "conflict",
        detail: "Two ledger candidates",
      },
      {
        label: "DATE",
        status: "verified",
        detail: "Within window",
      },
    ],
  },
  {
    id: "S021",
    reason: "MULTIPLE_CANDIDATES",
    confidence: "0.74",
    candidates: ["L151", "L154"],
    merchant: "MERCHANT_077",
    amount: "19,200.00",
    currency: "INR",
    reference: "PAY-55182",
    settlementDate: "2026-08-15",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "CURRENCY",
        status: "verified",
        detail: "INR",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Exact",
      },
      {
        label: "REFERENCE",
        status: "conflict",
        detail: "Duplicate reference candidate",
      },
    ],
  },
  {
    id: "S033",
    reason: "MULTIPLE_CANDIDATES",
    confidence: "0.69",
    candidates: ["L184", "L191"],
    merchant: "MERCHANT_061",
    amount: "5,600.00",
    currency: "INR",
    reference: "PAY-61027",
    settlementDate: "2026-08-16",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Within tolerance",
      },
      {
        label: "REFERENCE",
        status: "conflict",
        detail: "Two plausible candidates",
      },
      {
        label: "DATE",
        status: "verified",
        detail: "Within window",
      },
    ],
  },
  {
    id: "S052",
    reason: "MULTIPLE_CANDIDATES",
    confidence: "0.73",
    candidates: ["L241", "L249"],
    merchant: "MERCHANT_028",
    amount: "9,875.00",
    currency: "INR",
    reference: "PAY-71348",
    settlementDate: "2026-08-17",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Exact",
      },
      {
        label: "REFERENCE",
        status: "conflict",
        detail: "Two plausible ledger records",
      },
      {
        label: "CURRENCY",
        status: "verified",
        detail: "INR",
      },
    ],
  },
  {
    id: "S071",
    reason: "MULTIPLE_CANDIDATES",
    confidence: "0.66",
    candidates: ["L302", "L305"],
    merchant: "MERCHANT_095",
    amount: "14,300.00",
    currency: "INR",
    reference: "PAY-82041",
    settlementDate: "2026-08-18",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Within tolerance",
      },
      {
        label: "REFERENCE",
        status: "conflict",
        detail: "Multiple plausible candidates",
      },
      {
        label: "DATE",
        status: "verified",
        detail: "Within window",
      },
    ],
  },

  /* -----------------------------------------------------------
     WRONG MERCHANT — 5
     ----------------------------------------------------------- */

  {
    id: "S027",
    reason: "WRONG_MERCHANT",
    confidence: "0.32",
    candidates: ["L209"],
    merchant: "MERCHANT_117",
    amount: "8,920.00",
    currency: "INR",
    reference: "PAY-98134",
    settlementDate: "2026-08-15",
    aiInvoked: false,
    evidence: [
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Within tolerance",
      },
      {
        label: "CURRENCY",
        status: "verified",
        detail: "INR",
      },
      {
        label: "MERCHANT",
        status: "conflict",
        detail: "Ledger merchant differs",
      },
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
    ],
  },
  {
    id: "S047",
    reason: "WRONG_MERCHANT",
    confidence: "0.28",
    candidates: ["L224"],
    merchant: "MERCHANT_032",
    amount: "3,750.00",
    currency: "INR",
    reference: "PAY-21472",
    settlementDate: "2026-08-16",
    aiInvoked: false,
    evidence: [
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Exact",
      },
      {
        label: "MERCHANT",
        status: "conflict",
        detail: "Merchant identity mismatch",
      },
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
      {
        label: "DATE",
        status: "verified",
        detail: "Within window",
      },
    ],
  },
  {
    id: "S063",
    reason: "WRONG_MERCHANT",
    confidence: "0.35",
    candidates: ["L278"],
    merchant: "MERCHANT_088",
    amount: "11,600.00",
    currency: "INR",
    reference: "PAY-32981",
    settlementDate: "2026-08-17",
    aiInvoked: false,
    evidence: [
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Within tolerance",
      },
      {
        label: "MERCHANT",
        status: "conflict",
        detail: "Ledger merchant differs",
      },
      {
        label: "CURRENCY",
        status: "verified",
        detail: "INR",
      },
    ],
  },
  {
    id: "S081",
    reason: "WRONG_MERCHANT",
    confidence: "0.31",
    candidates: ["L344"],
    merchant: "MERCHANT_054",
    amount: "6,420.00",
    currency: "INR",
    reference: "PAY-48013",
    settlementDate: "2026-08-18",
    aiInvoked: false,
    evidence: [
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Exact",
      },
      {
        label: "CURRENCY",
        status: "verified",
        detail: "INR",
      },
      {
        label: "MERCHANT",
        status: "conflict",
        detail: "Merchant mismatch",
      },
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
    ],
  },
  {
    id: "S094",
    reason: "WRONG_MERCHANT",
    confidence: "0.26",
    candidates: ["L479"],
    merchant: "MERCHANT_120",
    amount: "15,250.00",
    currency: "INR",
    reference: "PAY-58872",
    settlementDate: "2026-08-19",
    aiInvoked: false,
    evidence: [
      {
        label: "MERCHANT",
        status: "conflict",
        detail: "Ledger identity mismatch",
      },
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Within tolerance",
      },
      {
        label: "DATE",
        status: "verified",
        detail: "Within window",
      },
    ],
  },

  /* -----------------------------------------------------------
     MISSING REFERENCE — 4
     ----------------------------------------------------------- */

  {
    id: "S041",
    reason: "MISSING_REFERENCE",
    confidence: "—",
    candidates: [],
    merchant: "MERCHANT_031",
    amount: "2,180.00",
    currency: "INR",
    reference: "—",
    settlementDate: "2026-08-15",
    aiInvoked: false,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Within tolerance",
      },
      {
        label: "REFERENCE",
        status: "missing",
        detail: "No usable reference",
      },
      {
        label: "DATE",
        status: "verified",
        detail: "Within window",
      },
    ],
  },
  {
    id: "S076",
    reason: "MISSING_REFERENCE",
    confidence: "—",
    candidates: [],
    merchant: "MERCHANT_012",
    amount: "4,900.00",
    currency: "INR",
    reference: "—",
    settlementDate: "2026-08-17",
    aiInvoked: false,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Exact",
      },
      {
        label: "REFERENCE",
        status: "missing",
        detail: "Reference absent from source",
      },
      {
        label: "DATE",
        status: "verified",
        detail: "Within window",
      },
    ],
  },
  {
    id: "S084",
    reason: "MISSING_REFERENCE",
    confidence: "—",
    candidates: [],
    merchant: "MERCHANT_063",
    amount: "1,875.00",
    currency: "INR",
    reference: "—",
    settlementDate: "2026-08-18",
    aiInvoked: false,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "CURRENCY",
        status: "verified",
        detail: "INR",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Within tolerance",
      },
      {
        label: "REFERENCE",
        status: "missing",
        detail: "No reference supplied",
      },
    ],
  },
  {
    id: "S097",
    reason: "MISSING_REFERENCE",
    confidence: "—",
    candidates: [],
    merchant: "MERCHANT_104",
    amount: "7,320.00",
    currency: "INR",
    reference: "—",
    settlementDate: "2026-08-19",
    aiInvoked: false,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Exact",
      },
      {
        label: "DATE",
        status: "verified",
        detail: "Within window",
      },
      {
        label: "REFERENCE",
        status: "missing",
        detail: "No usable source reference",
      },
    ],
  },

  /* -----------------------------------------------------------
     DATE LAG — 4
     ----------------------------------------------------------- */

  {
    id: "S068",
    reason: "DATE_LAG",
    confidence: "0.58",
    candidates: ["L307"],
    merchant: "MERCHANT_086",
    amount: "18,750.00",
    currency: "INR",
    reference: "PAY-44192",
    settlementDate: "2026-08-17",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Exact",
      },
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
      {
        label: "DATE",
        status: "conflict",
        detail: "Settlement +3 days from ledger",
      },
    ],
  },
  {
    id: "S071D",
    reason: "DATE_LAG",
    confidence: "0.61",
    candidates: ["L326"],
    merchant: "MERCHANT_043",
    amount: "9,450.00",
    currency: "INR",
    reference: "PAY-51204",
    settlementDate: "2026-08-18",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Within tolerance",
      },
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
      {
        label: "DATE",
        status: "conflict",
        detail: "Settlement +2 days from ledger",
      },
    ],
  },
  {
    id: "S088",
    reason: "DATE_LAG",
    confidence: "0.54",
    candidates: ["L391"],
    merchant: "MERCHANT_071",
    amount: "13,880.00",
    currency: "INR",
    reference: "PAY-60471",
    settlementDate: "2026-08-19",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "AMOUNT",
        status: "verified",
        detail: "Exact",
      },
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
      {
        label: "DATE",
        status: "conflict",
        detail: "Settlement +4 days from ledger",
      },
    ],
  },
  {
    id: "S099",
    reason: "DATE_LAG",
    confidence: "0.59",
    candidates: ["L512"],
    merchant: "MERCHANT_019",
    amount: "5,140.00",
    currency: "INR",
    reference: "PAY-73106",
    settlementDate: "2026-08-20",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "CURRENCY",
        status: "verified",
        detail: "INR",
      },
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
      {
        label: "DATE",
        status: "conflict",
        detail: "Settlement +2 days from ledger",
      },
    ],
  },

  /* -----------------------------------------------------------
     PARTIAL REFUND — 4
     ----------------------------------------------------------- */

  {
    id: "S093",
    reason: "PARTIAL_REFUND",
    confidence: "0.64",
    candidates: ["L441"],
    merchant: "MERCHANT_009",
    amount: "4,200.00",
    currency: "INR",
    reference: "PAY-77215",
    settlementDate: "2026-08-18",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
      {
        label: "AMOUNT",
        status: "conflict",
        detail: "Refund-adjusted amount",
      },
      {
        label: "DATE",
        status: "verified",
        detail: "Within window",
      },
    ],
  },
  {
    id: "S096",
    reason: "PARTIAL_REFUND",
    confidence: "0.62",
    candidates: ["L455"],
    merchant: "MERCHANT_035",
    amount: "6,780.00",
    currency: "INR",
    reference: "PAY-78142",
    settlementDate: "2026-08-18",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
      {
        label: "AMOUNT",
        status: "conflict",
        detail: "Partial refund adjustment",
      },
      {
        label: "CURRENCY",
        status: "verified",
        detail: "INR",
      },
    ],
  },
  {
    id: "S101",
    reason: "PARTIAL_REFUND",
    confidence: "0.67",
    candidates: ["L468"],
    merchant: "MERCHANT_052",
    amount: "3,560.00",
    currency: "INR",
    reference: "PAY-79531",
    settlementDate: "2026-08-19",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
      {
        label: "AMOUNT",
        status: "conflict",
        detail: "Net amount after refund",
      },
      {
        label: "DATE",
        status: "verified",
        detail: "Within window",
      },
    ],
  },
  {
    id: "S105",
    reason: "PARTIAL_REFUND",
    confidence: "0.63",
    candidates: ["L481"],
    merchant: "MERCHANT_081",
    amount: "10,240.00",
    currency: "INR",
    reference: "PAY-81428",
    settlementDate: "2026-08-20",
    aiInvoked: true,
    evidence: [
      {
        label: "MERCHANT",
        status: "verified",
        detail: "Matched",
      },
      {
        label: "REFERENCE",
        status: "verified",
        detail: "Reference found",
      },
      {
        label: "AMOUNT",
        status: "conflict",
        detail: "Refund-adjusted amount",
      },
      {
        label: "DATE",
        status: "verified",
        detail: "Within window",
      },
    ],
  },
];

const filters = [
  "ALL",
  "MULTIPLE_CANDIDATES",
  "WRONG_MERCHANT",
  "MISSING_REFERENCE",
  "DATE_LAG",
  "PARTIAL_REFUND",
] as const;

export default function ExceptionsPage() {
  const [selectedId, setSelectedId] =
    useState(exceptions[0].id);

  const [activeFilter, setActiveFilter] =
    useState<(typeof filters)[number]>("ALL");

  const filteredExceptions = useMemo(() => {
    if (activeFilter === "ALL") {
      return exceptions;
    }

    return exceptions.filter(
      (record) =>
        record.reason === activeFilter,
    );
  }, [activeFilter]);

  const selectedException =
    filteredExceptions.find(
      (record) => record.id === selectedId,
    ) ??
    filteredExceptions[0] ??
    exceptions[0];

  function selectFilter(
    filter: (typeof filters)[number],
  ) {
    setActiveFilter(filter);

    const nextRecords =
      filter === "ALL"
        ? exceptions
        : exceptions.filter(
            (record) =>
              record.reason === filter,
          );

    if (nextRecords.length > 0) {
      setSelectedId(nextRecords[0].id);
    }
  }

  const filterCounts: Record<
    (typeof filters)[number],
    number
  > = {
    ALL: 23,
    MULTIPLE_CANDIDATES: 6,
    WRONG_MERCHANT: 5,
    MISSING_REFERENCE: 4,
    DATE_LAG: 4,
    PARTIAL_REFUND: 4,
  };

  return (
    <section className="mx-auto max-w-[1500px]">
      {/* =====================================================
          HEADER
          ===================================================== */}

      <header className="border-b border-[var(--border)] pb-7">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <span className="border border-[var(--amber)] bg-[var(--amber-soft)] px-2 py-1 font-mono text-[8px] font-semibold tracking-[0.16em] text-[var(--amber)]">
                03
              </span>

              <span className="font-mono text-[9px] font-semibold tracking-[0.2em] text-[var(--ink-muted)]">
                EXCEPTION REVIEW
              </span>
            </div>

            <h1 className="mt-4 text-4xl font-semibold tracking-[-0.05em] text-[var(--ink)] sm:text-5xl">
              Exceptions
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--ink-muted)]">
              Records where the engine preserved uncertainty instead of
              forcing an unsafe automatic decision.
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="font-mono text-[8px] tracking-[0.15em] text-[var(--ink-muted)]">
                TOTAL REVIEW POPULATION
              </div>

              <div className="mt-1 font-mono text-2xl font-semibold tracking-[-0.03em] text-[var(--ink)]">
                96
              </div>

              <div className="mt-1 font-mono text-[7px] tracking-[0.1em] text-[var(--ink-muted)]">
                BENCHMARK CASES
              </div>
            </div>

            <div className="h-11 w-px bg-[var(--border)]" />

            <span className="border border-[var(--amber)] bg-[var(--amber-soft)] px-3 py-2 font-mono text-[8px] font-semibold tracking-[0.14em] text-[var(--amber)]">
              HUMAN REVIEW
            </span>
          </div>
        </div>
      </header>

      {/* =====================================================
          CORE MESSAGE
          ===================================================== */}

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.08fr_.92fr]">
        <div className="relative overflow-hidden border border-[var(--amber)] bg-[var(--amber-soft)] p-6 sm:p-8">
          <div className="absolute left-0 top-0 h-full w-1 bg-[var(--amber)]" />

          <div className="pl-3">
            <div className="font-mono text-[8px] font-semibold tracking-[0.2em] text-[var(--amber)]">
              CONTROL STATE
            </div>

            <h2 className="mt-4 max-w-2xl text-2xl font-semibold leading-tight tracking-[-0.035em] text-[var(--ink)] sm:text-3xl">
              Uncertainty is preserved, not hidden.
            </h2>

            <p className="mt-4 max-w-2xl text-sm leading-6 text-[var(--ink-soft)]">
              Human review means the available evidence did not meet the bar
              for safe automatic resolution. It is an intentional control
              state, not a system failure.
            </p>
          </div>
        </div>

        <div className="border border-[var(--border-dark)] bg-[var(--navy)] p-6 text-white sm:p-8">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[8px] tracking-[0.2em] text-[#91A1B1]">
              SAFETY SIGNAL
            </span>

            <span className="font-mono text-[8px] tracking-[0.13em] text-[var(--lime)]">
              BENCHMARK
            </span>
          </div>

          <div className="mt-7 flex items-end gap-3">
            <span className="font-mono text-5xl font-medium tracking-[-0.05em] text-[var(--lime)]">
              0.00%
            </span>

            <span className="mb-2 font-mono text-[8px] tracking-[0.1em] text-[#94A2B1]">
              FALSE AUTO-MATCH
            </span>
          </div>

          <p className="mt-4 max-w-md text-xs leading-5 text-[#8F9EAD]">
            No incorrect automatic match was observed in the measured
            synthetic benchmark.
          </p>

          <div className="mt-6 border-t border-[#35485F] pt-4 font-mono text-[8px] tracking-[0.1em] text-[#728397]">
            REVIEW ≠ FAILURE
          </div>
        </div>
      </div>

      {/* =====================================================
          FILTERS
          ===================================================== */}

      <div className="mt-6 border border-[var(--border)] bg-[var(--surface)] p-2 shadow-[var(--shadow-sm)]">
        <div className="flex gap-1 overflow-x-auto">
          {filters.map((filter) => {
            const active = activeFilter === filter;
            const count = filterCounts[filter];

            return (
              <button
                key={filter}
                type="button"
                onClick={() =>
                  selectFilter(filter)
                }
                className={[
                  "flex shrink-0 items-center gap-2 px-4 py-3 font-mono text-[8px] font-semibold tracking-[0.12em] transition-all",
                  active
                    ? "bg-[var(--navy)] text-white"
                    : "text-[var(--ink-muted)] hover:bg-[var(--surface-soft)] hover:text-[var(--ink)]",
                ].join(" ")}
              >
                {formatReason(filter)}

                <span
                  className={[
                    "px-1.5 py-0.5 text-[7px]",
                    active
                      ? "bg-[var(--navy-3)] text-[#D9E1E8]"
                      : "bg-[var(--surface-muted)] text-[var(--ink-muted)]",
                  ].join(" ")}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* =====================================================
          REVIEW WORKSPACE
          ===================================================== */}

      <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1fr)_430px]">
        {/* Queue */}

        <div className="overflow-hidden border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow-sm)]">
          <div className="flex flex-col gap-3 border-b border-[var(--border)] px-5 py-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="font-mono text-[8px] font-semibold tracking-[0.18em] text-[var(--ink-soft)]">
                REVIEW QUEUE
              </div>

              <div className="mt-1 text-xs text-[var(--ink-muted)]">
                {filteredExceptions.length} representative cases shown · 96
                total benchmark review cases
              </div>
            </div>

            <div className="flex items-center gap-3">
              <span className="border border-[var(--copper)]/50 bg-[var(--copper-soft)] px-2.5 py-1.5 font-mono text-[7px] font-semibold tracking-[0.12em] text-[var(--copper-dark)]">
                DEMO INSPECTION SET
              </span>

              <span className="hidden font-mono text-[8px] tracking-[0.1em] text-[var(--ink-muted)] sm:block">
                {filteredExceptions.length} / 96
              </span>
            </div>
          </div>

          {/* Desktop */}

          <div className="hidden overflow-x-auto md:block">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-[var(--border)] bg-[var(--surface-soft)]">
                  <th className="px-5 py-3 text-left font-mono text-[8px] font-semibold tracking-[0.13em] text-[var(--ink-muted)]">
                    RECORD
                  </th>

                  <th className="px-5 py-3 text-left font-mono text-[8px] font-semibold tracking-[0.13em] text-[var(--ink-muted)]">
                    ESCALATION REASON
                  </th>

                  <th className="px-5 py-3 text-left font-mono text-[8px] font-semibold tracking-[0.13em] text-[var(--ink-muted)]">
                    CONFIDENCE
                  </th>

                  <th className="px-5 py-3 text-left font-mono text-[8px] font-semibold tracking-[0.13em] text-[var(--ink-muted)]">
                    CANDIDATES
                  </th>

                  <th className="px-5 py-3 text-right font-mono text-[8px] font-semibold tracking-[0.13em] text-[var(--ink-muted)]">
                    INSPECT
                  </th>
                </tr>
              </thead>

              <tbody>
                {filteredExceptions.map(
                  (record) => {
                    const selected =
                      record.id ===
                      selectedException.id;

                    return (
                      <tr
                        key={record.id}
                        onClick={() =>
                          setSelectedId(record.id)
                        }
                        className={[
                          "cursor-pointer border-b border-[var(--border)] transition-colors",
                          selected
                            ? "bg-[var(--amber-soft)]"
                            : "hover:bg-[var(--surface-soft)]",
                        ].join(" ")}
                      >
                        <td className="px-5 py-4">
                          <div className="font-mono text-[10px] font-semibold text-[var(--ink)]">
                            {record.id}
                          </div>

                          <div className="mt-1 text-xs text-[var(--ink-muted)]">
                            {record.currency}{" "}
                            {record.amount}
                          </div>
                        </td>

                        <td className="px-5 py-4">
                          <ReasonBadge
                            reason={record.reason}
                          />
                        </td>

                        <td className="px-5 py-4">
                          <span className="font-mono text-xs font-medium text-[var(--ink)]">
                            {record.confidence}
                          </span>
                        </td>

                        <td className="px-5 py-4">
                          <div className="flex flex-wrap gap-1.5">
                            {record.candidates.length >
                            0 ? (
                              record.candidates.map(
                                (candidate) => (
                                  <span
                                    key={candidate}
                                    className="border border-[var(--border)] bg-[var(--surface-soft)] px-2 py-1 font-mono text-[8px] text-[var(--ink-soft)]"
                                  >
                                    {candidate}
                                  </span>
                                ),
                              )
                            ) : (
                              <span className="font-mono text-[8px] text-[var(--ink-muted)]">
                                NONE
                              </span>
                            )}
                          </div>
                        </td>

                        <td className="px-5 py-4 text-right">
                          <span
                            className={[
                              "font-mono text-[8px] font-semibold tracking-[0.12em]",
                              selected
                                ? "text-[var(--amber)]"
                                : "text-[var(--ink-muted)]",
                            ].join(" ")}
                          >
                            VIEW →
                          </span>
                        </td>
                      </tr>
                    );
                  },
                )}
              </tbody>
            </table>
          </div>

          {/* Mobile */}

          <div className="divide-y divide-[var(--border)] md:hidden">
            {filteredExceptions.map(
              (record) => {
                const selected =
                  record.id ===
                  selectedException.id;

                return (
                  <button
                    key={record.id}
                    type="button"
                    onClick={() =>
                      setSelectedId(record.id)
                    }
                    className={[
                      "block w-full p-5 text-left",
                      selected
                        ? "bg-[var(--amber-soft)]"
                        : "bg-[var(--surface)]",
                    ].join(" ")}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="font-mono text-[10px] font-semibold text-[var(--ink)]">
                          {record.id}
                        </div>

                        <div className="mt-1 text-xs text-[var(--ink-muted)]">
                          {record.currency}{" "}
                          {record.amount}
                        </div>
                      </div>

                      <span className="font-mono text-[8px] font-semibold text-[var(--amber)]">
                        VIEW →
                      </span>
                    </div>

                    <div className="mt-4">
                      <ReasonBadge
                        reason={record.reason}
                      />
                    </div>

                    <div className="mt-4 flex gap-8">
                      <MetricMini
                        label="CONFIDENCE"
                        value={record.confidence}
                      />

                      <MetricMini
                        label="CANDIDATES"
                        value={String(
                          record.candidates.length,
                        )}
                      />
                    </div>
                  </button>
                );
              },
            )}
          </div>

          {filteredExceptions.length === 0 && (
            <div className="p-10 text-center">
              <div className="font-mono text-[9px] tracking-[0.15em] text-[var(--ink-muted)]">
                NO REPRESENTATIVE CASES
              </div>
            </div>
          )}
        </div>

        {/* Detail */}

        <ExceptionDetail
          record={selectedException}
        />
      </div>

      {/* =====================================================
          FOOTER
          ===================================================== */}

      <div className="mt-8 flex flex-col gap-2 border-t border-[var(--border)] py-5 font-mono text-[8px] tracking-[0.08em] text-[var(--ink-muted)] sm:flex-row sm:items-center sm:justify-between">
        <span>
          {filteredExceptions.length} REPRESENTATIVE CASES · 96 TOTAL
          BENCHMARK REVIEW POPULATION
        </span>

        <span>
          HUMAN REVIEW IS A CONTROL STATE, NOT A FAILURE
        </span>
      </div>
    </section>
  );
}

/* =============================================================
   DETAIL PANEL
   ============================================================= */

function ExceptionDetail({
  record,
}: {
  record: ExceptionRecord;
}) {
  return (
    <aside className="h-fit overflow-hidden border border-[var(--navy)] bg-[var(--navy)] text-white shadow-[var(--shadow-md)] xl:sticky xl:top-[96px]">
      <div className="border-b border-[#35485F] px-6 py-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="font-mono text-[8px] tracking-[0.2em] text-[#91A1B1]">
              EXCEPTION DETAIL
            </div>

            <div className="mt-2 font-mono text-lg font-semibold">
              {record.id}
            </div>
          </div>

          <span className="border border-[#B7802A] bg-[#332A1A] px-2.5 py-1.5 font-mono text-[8px] font-semibold tracking-[0.12em] text-[#F0C978]">
            HUMAN REVIEW
          </span>
        </div>
      </div>

      <div className="p-6">
        {/* Why */}

        <div>
          <div className="font-mono text-[8px] tracking-[0.18em] text-[#8190A0]">
            WHY AUTOMATION STOPPED
          </div>

          <h2 className="mt-3 text-xl font-semibold tracking-[-0.025em]">
            {formatReason(record.reason)}
          </h2>

          <p className="mt-3 text-sm leading-6 text-[#AAB6C2]">
            The available evidence did not meet the threshold for a safe
            automatic decision.
          </p>
        </div>

        {/* Transaction */}

        <div className="mt-7 border-y border-[#35485F] py-5">
          <div className="grid grid-cols-2 gap-x-5 gap-y-6">
            <DarkDetail
              label="MERCHANT"
              value={record.merchant}
            />

            <DarkDetail
              label="AMOUNT"
              value={`${record.currency} ${record.amount}`}
            />

            <DarkDetail
              label="REFERENCE"
              value={record.reference}
            />

            <DarkDetail
              label="SETTLEMENT DATE"
              value={record.settlementDate}
            />

            <DarkDetail
              label="CONFIDENCE"
              value={record.confidence}
            />

            <DarkDetail
              label="CANDIDATES"
              value={String(
                record.candidates.length,
              )}
            />
          </div>
        </div>

        {/* Candidate set */}

        <div className="mt-7">
          <div className="font-mono text-[8px] tracking-[0.18em] text-[#8190A0]">
            CANDIDATE SET
          </div>

          <div className="mt-3">
            {record.candidates.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {record.candidates.map(
                  (candidate) => (
                    <span
                      key={candidate}
                      className="border border-[#455970] bg-[#15263A] px-3 py-2 font-mono text-[9px] text-[#D2DAE2]"
                    >
                      {candidate}
                    </span>
                  ),
                )}
              </div>
            ) : (
              <div className="border border-[#35485F] bg-[#15263A] px-3 py-3 font-mono text-[8px] text-[#78899A]">
                NO CANDIDATE AVAILABLE
              </div>
            )}
          </div>
        </div>

        {/* Evidence */}

        <div className="mt-7">
          <div className="font-mono text-[8px] tracking-[0.18em] text-[#8190A0]">
            EVIDENCE CHAIN
          </div>

          <div className="mt-3 divide-y divide-[#35485F] border border-[#35485F]">
            {record.evidence.map((item) => (
              <EvidenceRow
                key={item.label}
                item={item}
              />
            ))}
          </div>
        </div>

        {/* AI */}

        <div className="mt-7 border border-[#35485F] bg-[#15263A] p-4">
          <div className="flex items-center justify-between gap-4">
            <span className="font-mono text-[8px] tracking-[0.15em] text-[#8190A0]">
              AI RESOLUTION
            </span>

            <span
              className={[
                "font-mono text-[8px] font-semibold tracking-[0.12em]",
                record.aiInvoked
                  ? "text-[#72B8D0]"
                  : "text-[#718196]",
              ].join(" ")}
            >
              {record.aiInvoked
                ? "INVOCATED"
                : "NOT REQUIRED"}
            </span>
          </div>

          <p className="mt-3 text-xs leading-5 text-[#8FA0B0]">
            {record.aiInvoked
              ? "AI reasoning helped interpret ambiguity. Final authorization remained withheld."
              : "Deterministic checks were sufficient to withhold automatic resolution without AI escalation."}
          </p>
        </div>

        {/* Final action */}

        <div className="mt-7">
          <div className="font-mono text-[8px] tracking-[0.18em] text-[#8190A0]">
            FINAL ACTION
          </div>

          <div className="mt-3 flex items-center justify-between gap-4 border border-[#B7802A] bg-[#332A1A] px-4 py-4">
            <div>
              <div className="font-mono text-[9px] font-semibold tracking-[0.14em] text-[#F0C978]">
                HUMAN REVIEW
              </div>

              <div className="mt-1 font-mono text-[7px] tracking-[0.1em] text-[#B68D4B]">
                AUTHORIZATION WITHHELD
              </div>
            </div>

            <span
              className="font-mono text-lg text-[#D0A753]"
              aria-hidden="true"
            >
              !
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}

/* =============================================================
   EVIDENCE ROW
   ============================================================= */

function EvidenceRow({
  item,
}: {
  item: EvidenceItem;
}) {
  const indicator =
    item.status === "verified"
      ? "✓"
      : item.status === "conflict"
        ? "!"
        : "—";

  const indicatorColor =
    item.status === "verified"
      ? "text-[var(--lime)]"
      : item.status === "conflict"
        ? "text-[var(--amber)]"
        : "text-[#8190A0]";

  const stateLabel =
    item.status === "verified"
      ? "VERIFIED"
      : item.status === "conflict"
        ? "CONFLICT"
        : "MISSING";

  return (
    <div className="grid grid-cols-[20px_1fr_auto] items-center gap-3 px-4 py-3">
      <span
        className={`font-mono text-[10px] font-bold ${indicatorColor}`}
        aria-hidden="true"
      >
        {indicator}
      </span>

      <div>
        <div className="font-mono text-[8px] font-semibold tracking-[0.1em] text-[#D3DAE1]">
          {item.label}
        </div>

        <div className="mt-1 text-[10px] leading-4 text-[#7F90A1]">
          {item.detail}
        </div>
      </div>

      <span
        className={`font-mono text-[7px] font-semibold tracking-[0.1em] ${indicatorColor}`}
      >
        {stateLabel}
      </span>
    </div>
  );
}

/* =============================================================
   REASON BADGE
   ============================================================= */

function ReasonBadge({
  reason,
}: {
  reason: ExceptionType;
}) {
  const classes =
    reason === "WRONG_MERCHANT"
      ? "border-[var(--red)] bg-[var(--red-soft)] text-[var(--red)]"
      : reason === "MISSING_REFERENCE"
        ? "border-[var(--blue)] bg-[var(--blue-soft)] text-[var(--blue)]"
        : "border-[var(--amber)] bg-[var(--amber-soft)] text-[var(--amber)]";

  return (
    <span
      className={[
        "inline-flex items-center gap-1.5 border px-2.5 py-1.5 font-mono text-[7px] font-semibold tracking-[0.1em]",
        classes,
      ].join(" ")}
    >
      <span aria-hidden="true">!</span>
      {formatReason(reason)}
    </span>
  );
}

/* =============================================================
   MINI METRIC
   ============================================================= */

function MetricMini({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div>
      <div className="font-mono text-[7px] tracking-[0.12em] text-[var(--ink-muted)]">
        {label}
      </div>

      <div className="mt-1 font-mono text-xs font-semibold text-[var(--ink)]">
        {value}
      </div>
    </div>
  );
}

/* =============================================================
   DARK DETAIL
   ============================================================= */

function DarkDetail({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div>
      <div className="font-mono text-[7px] tracking-[0.13em] text-[#718196]">
        {label}
      </div>

      <div className="mt-1.5 truncate font-mono text-[9px] font-semibold text-[#DCE2E8]">
        {value}
      </div>
    </div>
  );
}

/* =============================================================
   FORMATTER
   ============================================================= */

function formatReason(
  value: string,
): string {
  return value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (char) =>
      char.toUpperCase(),
    );
}