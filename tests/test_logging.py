import json
import logging


from src.logging_config import JsonFormatter


def test_log_es_una_linea_json_con_sus_datos():
    record = logging.LogRecord("src.api", logging.INFO, __file__, 1, "ask", None, None)
    record.data = {"request_id": "abc", "cost_usd": 0.01}
    line = JsonFormatter().format(record)
    entry = json.loads(line)
    assert "\n" not in line
    assert (entry["msg"], entry["level"], entry["request_id"]) == ("ask","INFO", "abc")