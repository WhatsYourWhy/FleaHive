from FleaHive import summarize


def test_summarize_truncates_when_sentence_exceeds_max_len():
    long_sentence = (
        "This sentence is intentionally written to be quite long so that it exceeds the "
        "maximum length limit when summarized in a single pass without splitting."
    )
    summary = summarize(long_sentence, max_len=50, already_cleaned=True)
    assert summary.endswith("…")
    assert len(summary) == 51  # 50 chars + ellipsis


def test_summarize_handles_empty_input():
    summary = summarize("", max_len=100, already_cleaned=True)
    assert summary == "Nothing to summarize after cleaning."
