import io
import json
import re

from FleaHive import main


def test_main_outputs_json_with_compression(monkeypatch, capsys):
    text = (
        "This is a sufficiently long sentence to be captured in the summary output. "
        "Another informative sentence follows to give the summarizer more material."
    )
    monkeypatch.setattr("sys.stdin", io.StringIO(text))

    exit_code = main(["FleaHive.py", "-"])
    captured = capsys.readouterr().out
    result = json.loads(captured)

    assert exit_code == 0
    assert result["summary"]
    assert isinstance(result["tags"], list) and result["tags"]
    assert result["metrics"]["original_words"] > 0
    assert result["metrics"]["summary_words"] > 0
    assert re.match(r"^[0-9]+(?:\.[0-9])?%$", result["metrics"]["compression"])
