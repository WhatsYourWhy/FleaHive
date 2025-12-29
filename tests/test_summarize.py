import FleaHive
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


def test_summarize_preserves_short_sentences():
    text = "Short sentence. Tiny info."
    summary = summarize(text, max_len=100, already_cleaned=True)

    assert summary  # should not be empty
    assert "Short sentence." in summary or "Tiny info." in summary


def test_semantic_mode_prefers_closest_sentence(monkeypatch):
    text = (
        "An expansive discussion that covers many unrelated topics and keeps going well beyond the core idea. "
        "Key insight."
    )

    class FakeModel:
        def encode(self, values, normalize_embeddings=True):
            assert normalize_embeddings is True
            return [
                [1.0, 0.0],  # document vector
                [10.0, 4.0],  # expansive discussion (longer but less aligned)
                [1.0, 0.0],  # key insight (short but fully aligned)
            ]

    monkeypatch.setattr(FleaHive, "MODEL", FakeModel())

    summary = FleaHive.summarize(text, already_cleaned=True)

    assert summary.startswith("Key insight.")
