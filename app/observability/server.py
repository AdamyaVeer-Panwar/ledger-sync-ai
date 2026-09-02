from prometheus_client import start_http_server


DEFAULT_METRICS_PORT = 9000


def start_metrics_server(
    port: int = DEFAULT_METRICS_PORT,
):
    """
    Start the Prometheus metrics exposition server.

    The server runs independently from the reconciliation
    processing loop and exposes metrics at /metrics.
    """

    return start_http_server(port)