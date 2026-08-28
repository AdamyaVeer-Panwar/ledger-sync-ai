# LedgerSync AI — Evaluation Contract

## 1. Purpose

LedgerSync AI is evaluated as a financial reconciliation system, not simply as an AI generation system.

The evaluation must measure:

* correctness of reconciliation decisions
* safety of automated matching
* unresolved/exception cases
* system performance
* AI usage efficiency

The objective is:

> **Maximize correct automation while minimizing false financial matches.**

A safe exception is preferable to an incorrect match.

---

## 2. Evaluation Dataset

All reconciliation approaches are evaluated against the **same synthetic dataset** and the **same hidden ground truth**.

The dataset contains controlled financial scenarios:

1. EXACT_MATCH
2. ROUNDING_DIFFERENCE
3. DATE_LAG
4. MISSING_REFERENCE
5. DUPLICATE
6. PARTIAL_REFUND
7. MULTIPLE_CANDIDATES
8. WRONG_MERCHANT
9. MISSING_LEDGER
10. CORRUPTED_REFERENCE

Each settlement has a known expected outcome:

```text
settlement_id → [true ledger_id(s)]
settlement_id → null
```

`null` represents a true `NO_MATCH`.

A settlement may reconcile to zero, one, or multiple ledger records depending on the scenario.

---

## 3. Evaluation Baselines

Three approaches will be evaluated using the same input data and ground truth.

### 3.1 Rules-Only

Deterministic reconciliation logic with no LLM calls.

Goal:

* establish the performance of deterministic matching
* measure how much of the dataset can be safely resolved without AI

---

### 3.2 LLM-Only

The LLM receives the reconciliation context and produces a structured matching decision.

Goal:

* measure what an LLM can achieve without the deterministic fast path
* establish the accuracy, latency, and AI cost baseline

The LLM must operate on bounded candidate data rather than unrestricted access to the full dataset.

---

### 3.3 Hybrid

The production-oriented approach:

```text
Settlement
    ↓
Deterministic rules
    ↓
High-confidence match?
    ├── YES → MATCHED_RULE
    │
    └── NO
         ↓
    Candidate generation
         ↓
    Bounded LLM resolution
         ↓
    Policy / confidence gate
         ↓
    MATCHED_AI / HUMAN_REVIEW / NO_MATCH
```

The Hybrid approach is expected to minimize unnecessary LLM calls while preserving reconciliation accuracy.

---

# 4. Ground Truth

Ground truth is created during synthetic data generation and is not exposed to the reconciliation system.

Example:

```json
{
  "S000001": ["L000001"],
  "S000002": ["L000002", "L000003"],
  "S000003": null
}
```

Interpretation:

* `["L000001"]` → one true ledger match
* `["L000002", "L000003"]` → multiple true ledger records
* `null` → no valid ledger match exists

Ground truth is the reference against which every baseline is evaluated.

---

# 5. Core Accuracy Metrics

## 5.1 Precision

Precision measures how often predicted matches are correct.

```text
Precision =
Correct predicted matches
--------------------------------
All predicted matches
```

A high precision means the system is conservative and does not frequently produce incorrect matches.

---

## 5.2 Recall

Recall measures how many true matches the system successfully identifies.

```text
Recall =
Correct predicted matches
--------------------------------
All actual matches
```

A high recall means the system misses fewer valid reconciliation opportunities.

---

## 5.3 False-Match Rate

False-match rate measures how frequently the system produces an incorrect match.

```text
False-Match Rate =
Incorrect predicted matches
--------------------------------
All records evaluated
```

This is a critical safety metric because an incorrect financial match can be more harmful than an unresolved exception.

---

# 6. Exception Metrics

## 6.1 Exception Rate

The proportion of records that are not automatically resolved.

This includes cases routed to:

* HUMAN_REVIEW
* NO_MATCH

```text
Exception Rate =
Exceptions
----------------
Total records
```

---

## 6.2 Automation Rate

The proportion of records resolved automatically.

For the final system:

```text
Automation Rate =
MATCHED_RULE + MATCHED_AI
--------------------------------
Total records
```

A high automation rate is useful only when achieved without unacceptable false-match rates.

---

# 7. Performance Metrics

## 7.1 Latency

Latency measures the time required to process reconciliation decisions.

We will track:

* per-record latency
* batch latency

For AI-enabled paths, LLM latency will be measured separately where useful.

---

## 7.2 Throughput

Throughput measures the number of records processed per unit of time.

```text
Throughput =
Records processed
---------------------
Elapsed time
```

The same workload should be used when comparing baselines.

---

# 8. LLM Efficiency

## 8.1 LLM Call Rate

LLM call rate measures how much of the workload actually requires AI reasoning.

```text
LLM Call Rate =
Records sent to LLM
------------------------
Total records
```

Example:

```text
1,000 records
120 LLM calls

LLM Call Rate = 12%
```

This metric is particularly important for the Hybrid architecture.

A strong Hybrid system should resolve a large proportion of straightforward cases without invoking the LLM.

---

# 9. Safety Principle

The reconciliation system must prefer:

```text
uncertain → HUMAN_REVIEW / NO_MATCH
```

over:

```text
uncertain → incorrect MATCH
```

The evaluation therefore considers **false matching a higher-risk failure mode than unresolved matching**.

The system should not be optimized purely for the highest possible match rate.

---

# 10. Scenario-Level Evaluation

Overall metrics are not sufficient.

Performance must also be analysed by scenario.

Example:

```text
Scenario                Precision    Recall    Exceptions
----------------------------------------------------------
EXACT_MATCH             ...
ROUNDING_DIFFERENCE     ...
DATE_LAG                ...
MISSING_REFERENCE       ...
DUPLICATE               ...
PARTIAL_REFUND          ...
MULTIPLE_CANDIDATES     ...
WRONG_MERCHANT          ...
MISSING_LEDGER          ...
CORRUPTED_REFERENCE     ...
```

This allows failure analysis and prevents strong performance on easy cases from hiding weak performance on difficult cases.

---

# 11. Reproducibility

The synthetic dataset is generated with a deterministic seed.

Example:

```bash
python scripts/generate_data.py --records 400 --seed 42
```

The same seed and generation configuration must produce the same evaluation dataset.

All baselines must be evaluated against the same generated dataset and ground truth.

---

# 12. Evaluation Philosophy

The evaluation follows:

```text
Known data
    ↓
Known ground truth
    ↓
Run baseline
    ↓
Compare predictions with truth
    ↓
Calculate metrics
    ↓
Analyse failures
```

The system must be measured before conclusions about AI effectiveness are made.

The goal is not to prove that the LLM is useful.

The goal is to **measure when deterministic logic is sufficient, when AI adds value, and when the system should refuse to make a decision.**


## Rules-Only Baseline — 2026-08-29

Dataset:
- 400 settlement records
- Ground truth generated during Day 1
- Deterministic RuleMatcher
- In-memory candidate universe filtered by currency
- No LLM
- No external API calls
- No PostgreSQL candidate retrieval

| Metric | Result |
|---|---:|
| Records evaluated | 400 |
| Matched | 275 |
| Exceptions | 125 |
| Accuracy | 83.75% |
| Precision | 100.00% |
| Recall | 80.88% |
| False-match rate | 0.00% |
| Exception rate | 31.25% |
| Automation rate | 68.75% |
| Throughput | 4,107.94 records/sec |
| Elapsed time | 0.0974 sec |

### Interpretation

The deterministic baseline prioritizes safety over aggressive automation.

The system achieved 100% precision and 0% false-match rate on the evaluation dataset, while automatically resolving 68.75% of settlements.

The remaining 31.25% were treated as exceptions rather than being force-matched.

This establishes the rules-only baseline against which later candidate-retrieval and AI improvements will be evaluated.

### Benchmark boundary

The reported throughput measures the Day-3 in-memory evaluation setup. It is not a production-scale database retrieval benchmark.

Day 4 introduces indexed PostgreSQL candidate retrieval and measures search performance independently at larger ledger volumes.

## Candidate Retrieval Benchmark — Day 4

The candidate retrieval layer was benchmarked using synthetic PostgreSQL ledger datasets.

| Dataset | Query Time | Candidates |
|---:|---:|---:|
| 10,000 | 1.136 ms | 20 |
| 100,000 | 1.078 ms | 20 |

### PostgreSQL execution plan

The 100,000-record query used:

`ix_ledger_merchant_amount`

The query returned 20 actual rows and completed in 0.241 ms according to `EXPLAIN (ANALYZE, BUFFERS)`.

This demonstrates that candidate retrieval is bounded and database-backed rather than requiring a full ledger scan by the reasoning layer.

### Architecture

Settlement
→ CandidateRetriever
→ Indexed PostgreSQL query
→ bounded candidate set
→ RuleMatcher

The retrieval benchmark measures database candidate generation independently from reconciliation decision logic.