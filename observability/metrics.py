from prometheus_client import Counter, Histogram

# Prometheus Metric Definitions
LATENCY_HISTOGRAM = Histogram(
    "research_agent_request_duration_seconds",
    "Latency of research workflow executions in seconds",
    buckets=(5.0, 15.0, 30.0, 60.0, 120.0, 300.0, float("inf")),
)

TOKEN_USAGE_COUNTER = Counter(
    "research_agent_token_usage_total",
    "Total LLM token usage partitioned by model and type",
    ["model", "type"],  # type: "prompt" or "completion"
)

COST_COUNTER = Counter(
    "research_agent_cost_usd_total",
    "Cumulative estimated API cost of model requests in USD",
    ["model"],
)


def track_run_metrics(
    model: str, prompt_tokens: int, completion_tokens: int, latency_seconds: float
):
    """Tracks latency, token count, and calculated USD cost for a research task execution."""
    LATENCY_HISTOGRAM.observe(latency_seconds)
    TOKEN_USAGE_COUNTER.labels(model=model, type="prompt").inc(prompt_tokens)
    TOKEN_USAGE_COUNTER.labels(model=model, type="completion").inc(completion_tokens)

    # Pricing per 1M tokens
    cost = 0.0
    m_lower = model.lower()
    if "gpt-4o-mini" in m_lower:
        cost = (prompt_tokens * 0.15 / 1_000_000) + (
            completion_tokens * 0.60 / 1_000_000
        )
    elif "gpt-4o" in m_lower:
        cost = (prompt_tokens * 5.00 / 1_000_000) + (
            completion_tokens * 15.00 / 1_000_000
        )
    else:
        # Default fallback
        cost = (prompt_tokens * 0.15 / 1_000_000) + (
            completion_tokens * 0.60 / 1_000_000
        )

    COST_COUNTER.labels(model=model).inc(cost)
