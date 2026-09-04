# LedgerSync AI

Where AI reasons. Systems decide.

LedgerSync AI is an AI-assisted financial reconciliation controller built for the Razorpay AI Buildathon — Track 04: AI Finance Controller.
It compares settlement records with ledger records and produces controlled outcomes:
AUTO_MATCH · HUMAN_REVIEW · NO_MATCH

The system doesn't try to automate every decision. It automates the decisions it can prove, and exposes the rest as explicit exceptions.
The central design separates evidence from authority: deterministic rules establish what can be proven, candidate retrieval bounds the search space, AI is used only where reasoning is required, verification checks the proposal, and policy controls the final outcome.

## At a glance

Signal

Current verified result

Automated tests

161 passed

Benchmark records

400

Scenario types

10

Benchmark failures

0

Hybrid resolution accuracy

76.00%

Hybrid automation rate

76.00%

Auto-match precision

100.00%

Auto-match recall

89.41%

False auto-match rate

0.00%

Human review rate

24.00%

LLM invocations

90 / 400

LLM invocation rate

22.50%

P50 latency

78.01 ms

P95 latency

11.51 s

Total benchmark time

804.35 s

These results are from the current synthetic benchmark. They are not production accuracy, capacity, or SLO claims.

Problem

Reconciliation is not only record lookup. Real financial workflows contain ambiguity:

exact matches

rounding differences

date lag

missing references

duplicates

partial refunds

multiple candidates

wrong merchant identity

missing ledger entries

corrupted references
LedgerSync therefore asks two different questions:

What evidence supports a relationship?

Is the evidence strong enough to automate the outcome?
The project is built around the principle that maximum automation is not maximum correctness.

Architecture

flowchart TD
    A[Settlement Record] --> B[Normalize + Validate]
    B --> C[Candidate Retrieval]
    C --> D[Rule Matcher]
    D --> E{Evidence sufficient?}
    E -->|Yes| F[Policy Engine]
    E -->|No| G[Ollama / Qwen 2.5 3B]
    G --> H[LLM Proposal]
    H --> I[LLM Verification]
    I --> J[Evidence Fusion]
    J --> F
    F --> K[AUTO_MATCH]
    F --> L[HUMAN_REVIEW]
    F --> M[NO_MATCH]

The decision boundary is deliberate:

Deterministic evidence
        ↓
Can rules resolve safely?
   ┌────┴────┐
  YES        NO
   ↓          ↓
 Policy    Bounded AI
              ↓
         Verification
              ↓
         Evidence Fusion
              ↓
            Policy

Component authority

Component

Responsibility

Explicit boundary

RuleMatcher

Prove deterministic facts

Does not authorize outside policy

Candidate retrieval

Build bounded candidate set

Does not make the final decision

LLM resolver

Propose an interpretation

Cannot authorize financial action

LLMVerifier

Validate objective support

Cannot invent evidence

EvidenceFusion

Combine evidence

Cannot bypass verification

PolicyEngine

Choose allowed outcome

Cannot override missing/conflicting evidence

Persistence

Record state/evidence

Cannot manufacture an unverified result

AI reasons. Evidence constrains. Verification checks. Policy decides. The system records.

### Why Hybrid?

Approach

Strength

Main weakness

Rules-only

Fast, deterministic, explainable

Limited semantic coverage

LLM-only

Flexible semantic interpretation

Higher automated decision risk

Hybrid

Deterministic authority + selective AI + verification

More orchestration

Hybrid is not presented as the most accurate system overall. In the current benchmark, Rules-only has higher overall accuracy. Hybrid's value is the operating point between coverage, automation, AI dependency, and financial risk.

Current benchmark

Overall performance

System

Accuracy

Precision

Recall

False-match

Exceptions

Automation

P95

Rules

83.75%

88.71%

80.88%

0.00%

31.25%

68.75%

0.37 ms

LLM-only

67.50%

67.50%

79.41%

15.00%

0.00%

100.00%

11.62 s

Hybrid

76.00%

76.00%

89.41%

15.00%

24.00%

76.00%

11.51 s

Automation safety

System

Automation

Auto-match precision

False auto-match

Rules

68.75%

100.00%

0.00%

LLM-only

100.00%

67.50%

32.50%

Hybrid

76.00%

100.00%

0.00%

Metric distinction: false_match_rate is a broader resolution metric; false_auto_match_rate specifically measures incorrect matches that were automatically authorized. For safety claims, this README uses the latter.

#### Runtime profile

Metric

Rules

LLM-only

Hybrid

P50 latency

0.20 ms

7480.43 ms

78.01 ms

P95 latency

0.37 ms

11620.49 ms

11512.93 ms

Throughput

4,720.65 records/s

0.10 records/s

0.50 records/s

LLM invocation rate

0.00%

100.00%

22.50%

Failure rate

0.00%

0.00%

0.00%

The large Hybrid P50/P95 gap identifies the slower AI path as a clear future optimization target.

Scenario-driven evaluation

##### The dataset is deliberately constructed around known reconciliation conditions, not random noise:

EXACT_MATCH
ROUNDING_DIFFERENCE
DATE_LAG
MISSING_REFERENCE
DUPLICATE
PARTIAL_REFUND
MULTIPLE_CANDIDATES
WRONG_MERCHANT
MISSING_LEDGER
CORRUPTED_REFERENCE

Ground truth is generated before reconciliation:

Scenario definition
        ↓
Synthetic records ───→ Ground truth
        ↓
Reconciliation
        ↓
Prediction
        ↓
Prediction vs ground truth
        ↓
Metrics + failure analysis

Observed scenario behaviour

PARTIAL_REFUND

Rules

LLM-only

Hybrid

0.00%

100.00%

96.67%

MULTIPLE_CANDIDATES

Rules

LLM-only

Hybrid

---:

---:

---:

100.00%

0.00%

100.00%

Known current gaps include DUPLICATE, MISSING_LEDGER, and WRONG_MERCHANT. These are documented failure modes, not hidden cases.

Matching strategy

1. Candidate retrieval

The system creates a bounded candidate set using:

merchant identity

currency

amount tolerance: 0.02

date window: 2 days

reference information

candidate limit: 50

2. Deterministic rules

RuleMatcher is domain logic. It does not call the LLM, access the database, or depend on a web/API layer. It emits structured reconciliation state, candidate IDs, confidence/status information, and evidence codes.

3. AI proposal

Only unresolved records enter the AI path:

Provider: Ollama
Model:    qwen2.5:3b

The model receives structured settlement information and a bounded candidate set. Its output is parsed and validated as structured application data.

4. Verification

LLMVerifier performs deterministic checks such as candidate existence, merchant/currency compatibility, amount constraints, and payment/refund arithmetic.
For refund relationships:

net_amount = payment_total - refund_total

5. Policy

Evidence is combined before authorization:

STRONG_AGREEMENT → AUTO_MATCH
LLM_SUPPORTED    → AUTO_MATCH
AMBIGUOUS        → HUMAN_REVIEW
CONFLICT         → HUMAN_REVIEW
NO TRUSTWORTHY   → NO_MATCH

Raw LLM confidence is not financial authority.

AI runtime

Current verified provider/model:

Ollama
└── qwen2.5:3b

The latest Hybrid benchmark invoked the model for 90 / 400 records (22.50%). AI is therefore a selective dependency, not the default execution path.

Evaluation methodology

Three approaches are measured against the generated dataset and its ground truth:

Rules-only baseline
LLM-only baseline
Hybrid controller

Metrics include:

resolution accuracy

precision and recall

false-match rate

exception rate

automation rate

auto-match precision

false auto-match rate

LLM invocation rate

latency and throughput

failure rate
Versioned artifacts:

evaluation/results/
├── rules_baseline_results_v1.jsonl
├── ollama_baseline_results_v3.jsonl
└── hybrid_baseline_results_v2.jsonl

Generate the consolidated report with:

python -m evaluation.run

Testing

Final verified repository state:

161 passed
0 failed
0 warnings

The suite covers domain logic, normalization, validation, candidate retrieval, rule matching, Hybrid resolution, LLM verification, evidence fusion, policy, scenario generation, provider integrations, benchmark persistence, observability, repositories, and database constraints.
Run it with:

pytest

Observability

LedgerSync separates offline benchmark measurement from runtime telemetry:

Application
    ↓
Structured logging / metrics
    ↓
Prometheus
    ↓
Grafana

Demo UI

The frontend is a Next.js product surface at:

http://localhost:3001

Route

Purpose

/

Product overview

/run

Reconciliation workflow

/runs/[runId]

Run outcome and telemetry

/exceptions

Human review queue

/evaluation

Benchmark evidence

/engineering

Architecture and controls

Reviewer journey:

LANDING
  ↓
RUN 400-RECORD DEMO
  ↓
WATCH PIPELINE
  ↓
RUN SUMMARY
  ↓
EXCEPTIONS
  ↓
EVALUATION
  ↓
ENGINEERING

Frontend verification:

cd frontend
npm run lint
npm run build

Both final checks pass.

###### Local setup

Prerequisites

Python 3.10+

PostgreSQL

Docker / Docker Compose

Ollama

Node.js / npm

Install

git clone https://github.com/AdamyaVeer-Panwar/ledger-sync-ai.git
cd ledger-sync-ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

Configure .env from .env.example.

Database

alembic upgrade head

Ollama

ollama pull qwen2.5:3b

Smoke test:

ollama run qwen2.5:3b "Reply with exactly: LEDGERSYNC_OK"

Synthetic dataset

python scripts/generate_data.py --records 400 --seed 42 --output data

Test

pytest

Monitoring

docker compose up

Evaluation

python -m evaluation.run

Frontend

cd frontend
npm install
npm run dev -- -p 3001

###### Repository structure

ledger-sync-ai/
├── app/
│   ├── db/                 # persistence models/session
│   ├── domain/             # reconciliation semantics
│   ├── infrastructure/     # provider implementations
│   ├── observability/      # logs and metrics
│   ├── repositories/       # persistence access
│   └── services/           # orchestration
├── evaluation/             # benchmark runners/evaluator/results
├── frontend/               # Next.js UI
├── monitoring/             # Prometheus/Grafana configuration
├── prompts/                # model prompts
├── scripts/                # reproducible workflows
├── tests/                  # unit + integration tests
├── alembic/                # migrations
├── compose.yaml
├── pyproject.toml
└── README.md

The separation is intentional:

app/domain          → reconciliation semantics
evaluation/         → measurement
frontend/           → product surface
monitoring/         → runtime telemetry
scripts/            → reproducible workflows
tests/              → executable contracts

Evaluation integrity

The repository contains multiple benchmark artifacts generated during development. The current headline Hybrid numbers come from:

evaluation/results/hybrid_baseline_results_v2.jsonl

Limitations

LedgerSync AI is a technical functionality and evaluation demonstration, not production financial infrastructure.

The dataset is synthetic and scenario-driven.

There are no live bank/PSP integrations.

Thresholds require calibration on representative real data.

Local benchmark throughput/latency are not production capacity or SLO claims.

Provider failover and production-scale resilience are not established.

The current project does not claim an implemented CI/CD pipeline.

Production deployment would require stronger authentication, authorization, secrets management, encryption, PII handling, audit retention, access control, incident response, and compliance controls.

Future production path

CURRENT
Synthetic benchmark
161 tests
Bounded Ollama reasoning
PostgreSQL persistence
Prometheus + Grafana
Local operational UI
        ↓
NEXT
Representative historical corpus
Threshold calibration
Duplicate / refund policy improvements
CI regression
Load testing
Provider failover testing
Confidence calibration
        ↓
PRODUCTION
Live payment / bank integrations
Authenticated service boundary
Multi-provider resilience
SLOs and alerting
Horizontal scaling
Durable audit controls
Human operations workflow
Continuous benchmark regression

The next major improvement should be better evidence and better policy, not simply a larger model.

Engineering thesis

Do not give probabilistic software authority over decisions that can be constrained by deterministic evidence.

AI reasons.
    ↓
Evidence constrains.
    ↓
Verification checks.
    ↓
Policy decides.
    ↓
The system records.