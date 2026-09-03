# LedgerSync AI
Where AI reasons. Systems decide.
LedgerSync AI is an AI-assisted financial reconciliation controller that compares settlement records with ledger records and produces controlled outcomes:

AUTO_MATCH · HUMAN_REVIEW · NO_MATCH

The core design is deliberately hybrid: deterministic rules establish evidence, AI handles selected ambiguous relationships, deterministic verification checks the proposal, and policy controls the final outcome.

The LLM can propose an interpretation. It cannot authorize a financial outcome by itself.

At a glance
Signal	Current benchmark
Tests passed	161
Benchmark records	400
Scenarios	10
Benchmark failures	0.00%
Hybrid automation	76.00%
Hybrid auto-match precision	100.00%
Hybrid false auto-match	0.00%
Hybrid LLM invocation	22.50%
Hybrid accuracy	76.00%
These are results from the current synthetic benchmark. They are not claims about production financial accuracy.

1. Problem
Reconciliation is not just record lookup. Real operational conditions can break otherwise simple relationships:

Exact matches

Rounding differences

Date lag

Missing references

Duplicates

Partial refunds

Multiple candidates

Wrong merchant

Missing ledger entries

Corrupted references

The system must answer two separate questions:

What evidence supports a relationship?

Is that evidence strong enough to automate the outcome?

The project is built around a simple principle:

Maximizing automation is not equivalent to maximizing correctness.

2. Core architecture
flowchart TD
    A[Settlement Record] --> B[Candidate Retrieval]
    B --> C[Rule Matcher]
    C --> D{Evidence sufficient?}

    D -->|Yes| E[Policy Engine]
    E --> F[AUTO_MATCH]

    D -->|No| G[Ollama / Qwen 2.5 3B]
    G --> H[LLM Proposal]
    H --> I[LLM Verification]
    I --> J[Evidence Fusion]
    J --> K[Policy Engine]

    K --> F
    K --> L[HUMAN_REVIEW]
    K --> M[NO_MATCH]
The decision path is intentionally asymmetric:

Deterministic evidence
        ↓
Can rules resolve safely?
   ┌────┴────┐
  yes       no
   ↓         ↓
 Policy    Bounded AI
             ↓
        Verification
             ↓
        Evidence Fusion
             ↓
           Policy
3. Why hybrid?
Approach	Strength	Main risk
Rules-only	Fast, deterministic, explainable	Limited semantic coverage
LLM-only	Flexible interpretation	Can over-resolve unsafe cases
Hybrid	Deterministic authority + selective AI + verification	More orchestration
The benchmark makes the trade-off visible:

Rules accuracy: 83.75%

LLM-only accuracy: 67.50%

Hybrid accuracy: 76.00%

Hybrid recall: 89.41%

Hybrid auto-match precision: 100.00%

Hybrid false auto-match: 0.00%

So the hybrid system is not presented as more accurate overall than rules. Its current value is controlled automation with selective AI usage and an explicit safety boundary.

4. Current benchmark
Overall performance
System	Accuracy	Precision	Recall	False-match	Exceptions	Automation	P95
Rules	83.75%	88.71%	80.88%	0.00%	31.25%	68.75%	0.37 ms
LLM	67.50%	67.50%	79.41%	15.00%	0.00%	100.00%	11.62 s
Hybrid	76.00%	76.00%	89.41%	15.00%	24.00%	76.00%	11.51 s
Automation safety
System	Automation	Auto-match precision	False auto-match
Rules	68.75%	100.00%	0.00%
LLM	100.00%	67.50%	32.50%
Hybrid	76.00%	100.00%	0.00%
Terminology matters: the benchmark reports 15.00% overall false-match rate for Hybrid but 0.00% false auto-match. The second metric specifically measures incorrect outcomes that were automatically authorized.

Runtime metrics
Metric	Rules	LLM	Hybrid
P50 latency	0.20 ms	7480.43 ms	78.01 ms
P95 latency	0.37 ms	11620.49 ms	11512.93 ms
Throughput	4,720.65 records/s	0.10 records/s	0.50 records/s
LLM invocation rate	0.00%	100.00%	22.50%
Failure rate	0.00%	0.00%	0.00%
The Hybrid P95 is high because only a minority of cases enter the local LLM path, but those calls dominate the long tail.

5. Scenario-driven evaluation
The benchmark is deliberately constructed around known reconciliation conditions rather than random synthetic noise:

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
Each generated case has its expected relationship recorded at creation time.

Scenario definition
       ↓
Synthetic records ─────→ Ground truth
       ↓
Reconciliation system
       ↓
Prediction
       ↓
Prediction vs ground truth
       ↓
Metrics + failure analysis
Scenario metadata is evaluation metadata. It is not exposed to the matching logic as a shortcut.

6. What the benchmark found
The strongest evidence is in the scenario-level differences.

Partial refund
System	Accuracy
Rules	0.00%
LLM	100.00%
Hybrid	96.67%
The LLM provides useful semantic signal for the multi-record refund relationship, while Hybrid retains deterministic verification around the proposal.

Multiple candidates
System	Accuracy
Rules	100.00%
LLM	0.00%
Hybrid	100.00%
The system does not force the LLM to collapse deterministic ambiguity. When multiple candidates remain plausible, policy can preserve HUMAN_REVIEW.

Current gaps
Scenario	Rules	LLM	Hybrid
Duplicate	0.00%	0.00%	0.00%
Missing ledger	100.00%	0.00%	0.00%
Wrong merchant	100.00%	0.00%	0.00%
These are documented failure modes, not hidden benchmark cases.

7. Matching strategy
Candidate retrieval
The system first retrieves a bounded candidate set instead of giving the model unrestricted ledger access.

Current retrieval constraints include:

Merchant identity

Currency

Amount tolerance of 0.02

Date window of 2 days

Reference information

Maximum candidate limit of 50

Deterministic rules
RuleMatcher is business logic, not infrastructure. It does not call an LLM, access the database, or depend on the web/API layer.

It normalizes relevant fields and emits structured status, confidence, candidate IDs, and evidence codes.

AI proposal
Only unresolved cases reach the AI path.

Ollama
└── qwen2.5:3b
The model receives structured settlement data and a bounded candidate set. Its output is parsed and validated as structured application data rather than trusted as free-form text.

Verification
LLMVerifier is deterministic. It checks objective constraints such as:

Candidate IDs exist

Merchant compatibility

Currency compatibility

Amount equality where required

Payment/refund arithmetic

Multi-ledger arithmetic

For refund relationships, verification can check:

net_amount = payment_total - refund_total
Evidence fusion and policy
Evidence is combined from rules, AI, and verification before authorization.

STRONG_AGREEMENT → AUTO_MATCH
LLM_SUPPORTED    → AUTO_MATCH
AMBIGUOUS        → HUMAN_REVIEW
CONFLICT         → HUMAN_REVIEW
No trustworthy evidence → NO_MATCH
The policy does not treat raw LLM confidence as financial authority.

8. Decision authority
Component	Can do	Cannot do
RuleMatcher	Establish deterministic evidence	Authorize outside policy
LLM Resolver	Propose an interpretation	Authorize a transaction
LLMVerifier	Validate objective support	Invent evidence
EvidenceFusion	Combine evidence	Bypass verification
PolicyEngine	Select an allowed outcome	Override missing/conflicting evidence
Persistence	Record state and evidence	Manufacture an unverified decision
AI reasons. Evidence constrains. Verification checks. Policy decides. The system records.

9. Data model
At a high level, the domain is built around typed financial records and reconciliation outcomes:

SettlementRecord
├── settlement_id
├── merchant_id
├── amount
├── currency
├── settlement_date
└── reference?

LedgerRecord
├── ledger_id
├── merchant_id
├── amount
├── currency
├── transaction_type
├── posted_at
└── reference?

ReconciliationResult
├── status
├── matched IDs
├── confidence
├── evidence
└── audit information
Evaluation objects separately represent scenario context and expected outcomes.

10. Evaluation methodology
LedgerSync evaluates three paths against the same generated dataset:

Rules baseline
LLM-only baseline
Hybrid controller
Ground truth is created before reconciliation. The evaluator then measures aggregate and scenario-level behaviour.

Primary metrics include:

Accuracy

Precision

Recall

False-match rate

Exception rate

Automation rate

Auto-match precision

False auto-match rate

LLM invocation rate

Latency and throughput

Failure rate

Benchmark result artifacts are versioned under:

evaluation/results/
├── rules_baseline_results_v1.jsonl
├── ollama_baseline_results_v3.jsonl
└── hybrid_baseline_results_v2.jsonl
11. Testing
Current repository state:

161 tests passed
The suite covers domain behaviour, reconciliation logic, repositories, resolvers/providers, evaluation, observability, and persistence constraints.

161 passed
0 failed
Testing is treated as an executable contract for the controller rather than only a final QA step.

12. Observability
The project separates offline benchmark measurement from runtime telemetry.

Application
    ↓
Structured logging / metrics
    ↓
Prometheus
    ↓
Grafana
Runtime monitoring is used for signals such as:

# Prometheus: http://localhost:9090

# Grafana: http://localhost:3000

Processing behaviour

Latency

Throughput

LLM invocations

Failures

Operational exceptions

The benchmark answers “how correct was the system?” while observability answers “how is the system behaving?”

13. Local setup
Prerequisites
Python 3.10+

PostgreSQL

Ollama

Docker Desktop/Engine

Install
# git clone https://github.com/AdamyaVeer-Panwar/ledger-sync-ai.git
cd ledger-sync-ai

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
Configure .env from .env.example, then apply migrations:

alembic upgrade head
Start the local model:

ollama pull qwen2.5:3b
Generate the reproducible dataset:

python scripts/generate_data.py --records 400 --seed 42 --output data
Run tests:

# pytest
# Start the monitoring stack:

# docker compose up
Run the current persisted benchmark evaluation:

python -m evaluation.run

14. Demo UI
The local frontend runs at:

# http://localhost:3001
It is organized around the reconciliation workflow rather than a chatbot:

Area	Purpose
Run	Execute and inspect reconciliation behaviour
Run Demo	Show the prepared end-to-end flow
Run Summary	Aggregate results
Exceptions	Review unresolved/unsafe cases
Evaluation	Show benchmark evidence
Engineering	Explain architecture and controls
The UI is a presentation and operations surface. It does not replace the domain policy layer.

15. Project structure
ledger-sync-ai/
├── app/
│   ├── db/
│   ├── domain/
│   │   ├── ai/
│   │   ├── reconciliation/
│   │   └── synthetic/
│   ├── infrastructure/
│   │   └── llm/
│   ├── observability/
│   ├── repositories/
│   └── services/
├── evaluation/
├── frontend/
├── monitoring/
├── prompts/
├── scripts/
├── tests/
├── alembic/
├── compose.yaml
├── pyproject.toml
└── README.md
The separation is intentional:

app/domain        → reconciliation semantics
app/repositories  → persistence
app/infrastructure→ provider implementations
app/services      → orchestration
evaluation/       → measurement
frontend/         → UI
monitoring/       → operational telemetry
scripts/          → reproducible workflows
tests/            → executable contracts
16. Evaluation integrity
The repository keeps benchmark artifacts for Rules, LLM-only, and Hybrid runs. The headline numbers above come from the current persisted result set reported by:

# python -m evaluation.run
The evaluation separates:

Dataset
Scenario definition
Ground truth
System version
Result artifact
Evaluation run
Changing the dataset, scenario distribution, model, prompt, thresholds, or metric definitions can change the benchmark. Results should therefore always be reported with their artifact/version context.

17. Limitations
LedgerSync AI is a technical functionality and evaluation demonstration, not a production financial infrastructure platform.

Synthetic data
The benchmark is scenario-driven synthetic data. It provides controlled ground truth but does not reproduce the full distribution, noise, operational edge cases, or data quality of real financial systems.

No live integrations
There is no live bank or payment-provider integration in the current build.

LLM dependency
The primary AI path uses local Ollama / qwen2.5:3b. An OpenAI provider is available as an emergency/alternative provider path. Model behaviour, latency, availability, and output quality therefore depend on provider configuration.

Threshold calibration
Matching tolerances are benchmark parameters. They require calibration against representative real reconciliation data before production use.

Performance scope
Local benchmark throughput and latency are not production capacity or SLO claims.

CI/CD scope
The project does not currently claim an implemented CI/CD pipeline.

Security and compliance
Production deployment would require stronger controls for authentication, authorization, secrets, encryption, PII handling, audit retention, access control, incident response, and compliance.

18. Future production path
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
Duplicate/refund policy improvements
CI regression suite
Load testing
Provider failover testing
Confidence calibration

        ↓

PRODUCTION
Live payment/bank integrations
Authenticated service boundary
Multi-provider resilience
SLOs and alerting
Horizontal scaling
Durable audit controls
Human operations workflow
Continuous benchmark regression
The next major improvement should be better evidence and better policy, not simply a larger model.

Engineering thesis
LedgerSync is built around one principle:

Do not give probabilistic software authority over decisions that can be constrained by deterministic evidence.

The system therefore keeps the responsibilities separate:

AI reasons.
    ↓
Evidence constrains.
    ↓
Verification checks.
    ↓
Policy decides.
    ↓
The system records.
