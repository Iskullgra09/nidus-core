import json
import logging

from app.core.logging import JsonFormatter, configure_logging
from app.core.request_context import RequestContext


def test_json_formatter_includes_request_context() -> None:
    configure_logging()
    RequestContext.reset()
    RequestContext.set_request_id("req-123")
    RequestContext.set_client_ip("127.0.0.1")

    record = logging.LogRecord(
        name="nidus.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.method = "GET"
    record.path = "/api/v1/health"
    record.status_code = 200
    record.latency_ms = 1.5

    payload = json.loads(JsonFormatter().format(record))
    assert payload["msg"] == "hello"
    assert payload["request_id"] == "req-123"
    assert payload["client_ip"] == "127.0.0.1"
    assert payload["method"] == "GET"
    assert payload["path"] == "/api/v1/health"
    assert payload["status_code"] == 200
    assert payload["latency_ms"] == 1.5

    RequestContext.reset()
