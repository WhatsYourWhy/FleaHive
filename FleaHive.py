#!/usr/bin/env python3
# FleaHive — Best local paper / notes / book summarizer 2025
# Drag any .txt onto this file → instant summary + tags + stats
# 100% offline · zero accounts · zero cost

import importlib.util
import json
import math
import re
import sys
from collections import Counter
from typing import Iterable, List, Sequence


def load_model():
    """Load the optional embedding model, but only if its dependencies are present."""
    if not importlib.util.find_spec("sentence_transformers"):
        return None
    if not importlib.util.find_spec("torch"):
        return None

    from sentence_transformers import SentenceTransformer

    try:
        return SentenceTransformer(
            "all-MiniLM-L6-v2",
            device="cpu",
            local_files_only=True,  # fall back immediately if model weights are not cached
        )
    except Exception:
        return None


MODEL = load_model()


def _cosine_similarity(vec_a: Iterable[float], vec_b: Iterable[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if not norm_a or not norm_b:
        return 0.0
    return float(dot / (norm_a * norm_b))


def _l2_normalize(vec: Iterable[float]) -> List[float]:
    norm = math.sqrt(sum(component * component for component in vec))
    if not norm:
        return list(vec)
    return [component / norm for component in vec]


def clean(text: str) -> str:
    """Normalize Markdown-heavy text before summarization."""
    text = re.sub(r"(?s)\A---\s*\n.*?\n---\s*\n?", "", text, count=1)  # frontmatter
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # links
    text = re.sub(r"(?i)@article{[^}]+}|https?://\S+|doi:\S+", "", text)  # refs/urls
    text = re.sub(r"!\[.*?\]\([^\)]+\)", "", text)  # images
    text = re.sub(r"[*#>`~]", "", text)  # markdown symbols
    text = re.sub(r"^Table\s*\d+.*|^Figure\s*\d+.*", "", text, flags=re.M | re.I)  # fig/table

    cutoff = re.search(r"(?i)\n\s*(references|bibliography|appendix)\s*\n", text)
    if cutoff:
        text = text[: cutoff.start()]

    return text.strip()


def split_sentences(text: str) -> List[str]:
    """Simple sentence splitter that preserves meaningful fragments."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    # If punctuation-based splitting fails (e.g., no sentence-ending punctuation), fall back
    # to the entire text so short passages still summarize properly.
    if not sentences and text.strip():
        sentences = [text.strip()]
    return sentences


def summarize(text: str, max_len: int = 450, *, already_cleaned: bool = False) -> str:
    cleaned = text if already_cleaned else clean(text)
    sentences = split_sentences(cleaned)
    if not sentences and cleaned:
        sentences = [cleaned]
    if not sentences:
        return "Nothing to summarize after cleaning."

    if MODEL:  # semantic mode — compares every sentence to the whole document
        try:
            embeddings = MODEL.encode([cleaned] + sentences, normalize_embeddings=True)
        except TypeError:  # older models may not support the kwarg
            embeddings = MODEL.encode([cleaned] + sentences)

        normalized_embeddings = [_l2_normalize(emb) for emb in embeddings]
        doc_vec = normalized_embeddings[0]
        scores = [
            _cosine_similarity(doc_vec, sentence_vec) for sentence_vec in normalized_embeddings[1:]
        ]
        ranked = sorted(zip(scores, sentences), reverse=True)
    else:  # pure keyword mode (still excellent)
        words = re.findall(r"\w+", cleaned.lower())
        common = {w for w, _ in Counter(words).most_common(20) if len(w) > 4}
        ranked = sorted(
            [(sum(w[:5] in s.lower() for w in common), s) for s in sentences],
            reverse=True,
        )

    result: List[str] = []
    used = 0
    for _, sentence in ranked:
        if used + len(sentence) <= max_len:
            result.append(sentence)
            used += len(sentence)
        else:
            break
    return " ".join(result) or cleaned[:max_len] + "…"


def tag(text: str, top: int = 8) -> List[str]:
    words = re.findall(r"\w+", text.lower())
    stop = {
        "the",
        "and",
        "for",
        "with",
        "this",
        "that",
        "from",
        "were",
        "been",
        "have",
        "using",
        "used",
        "which",
        "their",
        "they",
        "will",
        "would",
        "there",
        "these",
        "about",
        "when",
        "what",
        "where",
        "is",
        "are",
        "was",
        "not",
        "but",
        "all",
        "into",
        "can",
        "has",
        "more",
        "one",
        "its",
        "out",
        "also",
        "than",
        "other",
        "some",
        "very",
        "only",
        "time",
        "just",
        "even",
        "most",
        "like",
        "may",
        "such",
        "each",
        "new",
        "based",
        "our",
        "results",
        "study",
        "method",
        "approach",
        "proposed",
    }
    candidates = [w for w in words if w not in stop and len(w) > 3]
    return [word for word, _ in Counter(candidates).most_common(top)]


def main(argv: Sequence[str]) -> int:
    if len(argv) < 2:
        print(json.dumps({"error": "Drag a .txt or .md file here, or pipe text in"}))
        return 1

    path = argv[1]
    try:
        text = sys.stdin.read() if path == "-" else open(path, "r", encoding="utf-8").read()
    except Exception as exc:  # pragma: no cover - CLI error surface
        print(json.dumps({"error": str(exc)}))
        return 1

    cleaned_text = clean(text)
    summary = summarize(cleaned_text, already_cleaned=True)
    tags = tag(summary + " " + cleaned_text)

    original_words = len(re.findall(r"\w+", text))
    summary_words = len(re.findall(r"\w+", summary))
    compression_ratio = summary_words / original_words if original_words else 0

    result = {
        "summary": summary,
        "tags": tags,
        "metrics": {
            "original_words": original_words,
            "summary_words": summary_words,
            "compression": f"{compression_ratio:.1%}",
        },
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
