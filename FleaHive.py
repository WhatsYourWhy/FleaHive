#!/usr/bin/env python3
# FleaHive — Best local paper / notes / book summarizer 2025
# Drag any .txt onto this file → instant summary + tags + stats
# 100% offline · zero accounts · zero cost

import importlib.util
import json
import math
import os
import re
import sys
from collections import Counter
from typing import Dict, Iterable, List, Sequence, Union


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


def _sentence_spans(text: str) -> List[Dict[str, Union[int, str]]]:
    spans: List[Dict[str, Union[int, str]]] = []
    start = 0

    for match in re.finditer(r"(?<=[.!?])\s+", text):
        end = match.start()
        segment = text[start:end]
        stripped = segment.strip()
        if stripped:
            leading = len(segment) - len(segment.lstrip())
            trailing = len(segment) - len(segment.rstrip())
            spans.append(
                {
                    "text": stripped,
                    "index": len(spans),
                    "start": start + leading,
                    "end": end - trailing,
                }
            )
        start = match.end()

    segment = text[start:]
    stripped = segment.strip()
    if stripped:
        leading = len(segment) - len(segment.lstrip())
        trailing = len(segment) - len(segment.rstrip())
        spans.append(
            {
                "text": stripped,
                "index": len(spans),
                "start": start + leading,
                "end": start + len(segment) - trailing,
            }
        )

    if not spans and text.strip():
        stripped_all = text.strip()
        leading = len(text) - len(text.lstrip())
        trailing = len(text) - len(text.rstrip())
        spans.append(
            {
                "text": stripped_all,
                "index": 0,
                "start": leading,
                "end": len(text) - trailing,
            }
        )

    return spans


def summarize(
    text: str,
    max_len: int = 450,
    *,
    already_cleaned: bool = False,
    include_anchors: bool = False,
) -> Union[str, Dict[str, Union[str, List[Dict[str, Union[int, str]]]]]]:
    cleaned = text if already_cleaned else clean(text)
    sentences_with_spans = _sentence_spans(cleaned)
    sentences = [entry["text"] for entry in sentences_with_spans]
    if not sentences_with_spans and cleaned:
        sentences_with_spans = [
            {"text": cleaned, "index": 0, "start": 0, "end": len(cleaned)}
        ]
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
        ranked = sorted(zip(scores, sentences_with_spans), reverse=True)
    else:  # pure keyword mode (still excellent)
        words = re.findall(r"\w+", cleaned.lower())
        common = {w for w, _ in Counter(words).most_common(20) if len(w) > 4}
        ranked = sorted(
            [
                (sum(w[:5] in entry["text"].lower() for w in common), entry)
                for entry in sentences_with_spans
            ],
            reverse=True,
        )

    result: List[str] = []
    anchors: List[Dict[str, Union[int, str]]] = []
    used = 0
    for _, entry in ranked:
        sentence = entry["text"]
        if used + len(sentence) <= max_len:
            result.append(sentence)
            anchors.append(
                {
                    "sentence": sentence,
                    "source_index": entry["index"],
                    "start": entry["start"],
                    "end": entry["end"],
                }
            )
            used += len(sentence)
        else:
            break
    summary_text = " ".join(result) or cleaned[:max_len] + "…"

    if not include_anchors:
        return summary_text

    return {"text": summary_text, "anchors": anchors}


def tag(
    text: str,
    top: int = 8,
    *,
    include_anchors: bool = False,
    source_text: str | None = None,
) -> Union[List[str], List[Dict[str, Union[int, str, None]]]]:
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
    tags = [word for word, _ in Counter(candidates).most_common(top)]

    if not include_anchors:
        return tags

    anchor_text = (source_text or text).lower()
    anchored_tags: List[Dict[str, Union[int, str, None]]] = []
    for word in tags:
        match = re.search(rf"\b{re.escape(word)}\b", anchor_text)
        anchored_tags.append(
            {
                "tag": word,
                "position": match.start() if match else None,
            }
        )

    return anchored_tags


def main(argv: Sequence[str]) -> int:
    include_anchors = bool(os.getenv("FLEAHIVE_INCLUDE_ANCHORS"))
    args = list(argv[1:])
    if any(flag in args for flag in ("-a", "--include-anchors")):
        include_anchors = True
        args = [arg for arg in args if arg not in ("-a", "--include-anchors")]

    output_md_path: str | None = None
    if "--output-md" in args:
        idx = args.index("--output-md")
        if idx + 1 < len(args) and not args[idx + 1].startswith("-"):
            output_md_path = args[idx + 1]
            del args[idx : idx + 2]
        else:
            output_md_path = ""
            del args[idx]

    if not args:
        print(json.dumps({"error": "Drag a .txt or .md file here, or pipe text in"}))
        return 1

    path = args[0]
    try:
        text = sys.stdin.read() if path == "-" else open(path, "r", encoding="utf-8").read()
    except Exception as exc:  # pragma: no cover - CLI error surface
        print(json.dumps({"error": str(exc)}))
        return 1

    cleaned_text = clean(text)
    summary_result = summarize(cleaned_text, already_cleaned=True, include_anchors=include_anchors)
    if isinstance(summary_result, dict):
        summary_text = summary_result["text"]
        evidence = {"summary": summary_result.get("anchors", [])}
    else:
        summary_text = summary_result
        evidence = {}

    tag_result = tag(
        summary_text + " " + cleaned_text,
        include_anchors=include_anchors,
        source_text=cleaned_text,
    )
    if isinstance(tag_result, list) and tag_result and isinstance(tag_result[0], dict):
        tags = [entry["tag"] for entry in tag_result]  # type: ignore[index]
        evidence["tags"] = tag_result
    else:
        tags = tag_result  # type: ignore[assignment]

    original_words = len(re.findall(r"\w+", text))
    summary_words = len(re.findall(r"\w+", summary_text))
    compression_ratio = summary_words / original_words if original_words else 0

    result = {
        "summary": summary_text,
        "tags": tags,
        "metrics": {
            "original_words": original_words,
            "summary_words": summary_words,
            "compression": f"{compression_ratio:.1%}",
        },
    }

    if include_anchors:
        result["evidence"] = evidence

    if output_md_path is not None:
        frontmatter_tags = ", ".join(tags)
        markdown_lines = [
            "---",
            f"tags: [{frontmatter_tags}]",
            f"original_words: {original_words}",
            f"summary_words: {summary_words}",
            f"compression: \"{compression_ratio:.1%}\"",
            "---",
            "",
            "## Summary",
            summary_text,
        ]
        if include_anchors:
            markdown_lines.extend(
                [
                    "",
                    "## Evidence",
                    "```json",
                    json.dumps(evidence, indent=2, ensure_ascii=False),
                    "```",
                ]
            )
        markdown_output = "\n".join(markdown_lines).strip() + "\n"
        if output_md_path:
            with open(output_md_path, "w", encoding="utf-8") as handle:
                handle.write(markdown_output)
        print(markdown_output, end="")
        return 0

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
