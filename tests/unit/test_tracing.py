from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)


def test_tracer_can_create_span():
    exporter = InMemorySpanExporter()

    provider = TracerProvider()

    provider.add_span_processor(
        SimpleSpanProcessor(exporter)
    )

    tracer = provider.get_tracer(
        "ledgersync.test"
    )

    with tracer.start_as_current_span(
        "reconciliation.record"
    ) as span:
        span.set_attribute(
            "run_id",
            123,
        )

        span.set_attribute(
            "settlement_id",
            "S001",
        )

    spans = exporter.get_finished_spans()

    assert len(spans) == 1

    finished_span = spans[0]

    assert (
        finished_span.name
        == "reconciliation.record"
    )

    assert (
        finished_span.attributes["run_id"]
        == 123
    )

    assert (
        finished_span.attributes["settlement_id"]
        == "S001"
    )