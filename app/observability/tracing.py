"""
OpenTelemetry tracing configuration for LedgerSync AI.

This module owns tracing infrastructure only.

Business code should:
    from app.observability.tracing import get_tracer

and create spans around meaningful application operations.

Current configuration:
    - OpenTelemetry SDK
    - Console exporter for local development
    - Batch span processor
    - service.name resource attribute

A production deployment can later replace the console exporter
with an OTLP exporter without changing business instrumentation.
"""

from __future__ import annotations

import os

from opentelemetry import trace
from opentelemetry.sdk.resources import (
    Resource,
)
from opentelemetry.sdk.trace import (
    TracerProvider,
)
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

SERVICE_NAME = os.getenv(
    "OTEL_SERVICE_NAME",
    "ledgersync-ai",
)

_TRACER_NAME = "ledgersync.reconciliation"


def configure_tracing() -> None:
    """
    Configure the application's global OpenTelemetry tracer provider.

    This function should be called once during application startup.

    Console export is intentionally used for the current local
    development phase. A production deployment can later switch
    to OTLP without changing application-level span creation.
    """

    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": SERVICE_NAME,
            }
        )
    )

    processor = BatchSpanProcessor(
        ConsoleSpanExporter()
    )

    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)


def get_tracer() -> trace.Tracer:
    """
    Return the application's reconciliation tracer.

    Business/application code should use this function rather
    than constructing tracer providers itself.
    """

    return trace.get_tracer(
        _TRACER_NAME
    )