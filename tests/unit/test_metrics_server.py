from unittest.mock import patch

from app.observability.server import (
    DEFAULT_METRICS_PORT,
    start_metrics_server,
)


def test_metrics_server_uses_default_port():
    with patch(
        "app.observability.server.start_http_server"
    ) as mock_server:
        start_metrics_server()

    mock_server.assert_called_once_with(
        DEFAULT_METRICS_PORT
    )