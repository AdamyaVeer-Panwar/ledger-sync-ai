from prometheus_client import Counter, Histogram


reconciliation_records_total = Counter(
    "reconciliation_records_total",
    "Total number of reconciliation records processed.",
)

reconciliation_matches_total = Counter(
    "reconciliation_matches_total",
    "Total number of reconciliation records resolved automatically.",
)

reconciliation_exceptions_total = Counter(
    "reconciliation_exceptions_total",
    "Total number of reconciliation records requiring exception handling.",
)

candidate_retrieval_total = Counter(
    "candidate_retrieval_total",
    "Total number of candidate retrieval operations.",
)

candidate_retrieval_empty_total = Counter(
    "candidate_retrieval_empty_total",
    "Total number of candidate retrieval operations returning no candidates.",
)

candidate_retrieval_duration_seconds = Histogram(
    "candidate_retrieval_duration_seconds",
    "Candidate retrieval duration in seconds.",
)

candidate_retrieval_candidates = Histogram(
    "candidate_retrieval_candidates",
    "Number of candidates returned per retrieval operation.",
    buckets=(0, 1, 2, 5, 10, 20, 50),
)

llm_calls_total = Counter(
    "llm_calls_total",
    "Total number of LLM invocation attempts.",
)

llm_failures_total = Counter(
    "llm_failures_total",
    "Total number of failed LLM operations.",
)

reconciliation_duration_seconds = Histogram(
    "reconciliation_duration_seconds",
    "Reconciliation record processing duration in seconds.",
)

llm_latency_seconds = Histogram(
    "llm_latency_seconds",
    "LLM request latency in seconds.",
)