# Strainer 🧺

Offline document summarization + tagging for text and Markdown.

Strainer is a small, local-first CLI that converts .txt and .md files into structured summaries, tags, and metrics—entirely offline. It’s built for pipelines and note systems, not dashboards.

- Input: text / Markdown
- Output: JSON (default) or Obsidian-friendly Markdown
- Network: none (no API calls, no uploads)

## Privacy (offline-first)

Strainer runs fully offline: it makes zero network calls and never uploads your data.

---

## Why it exists

Most summarizers assume a web app and cloud processing. Strainer is for situations where notes must stay local and output needs to be reusable and inspectable.

Use Strainer when you want:

- Fast compression of long notes into a usable digest
- Tags you can feed into search / indexing
- Output that drops into scripts, vaults, or agents
- Offline operation by default

---

## Output

Strainer produces:

- Extractive summary (top-ranked sentences from the source)
- Tags (topic keywords)
- Metrics (word counts + compression)

Optional:

- Evidence anchors mapping summary sentences and tags back to the cleaned source text

---

## How it works

Strainer supports two modes. The output format is the same either way.

| Mode | Dependencies | Ranking approach | Speed |
| --- | --- | --- | --- |
| Smart (optional) | sentence-transformers, torch, numpy | Embedding-based sentence ranking | Slower, higher quality |
| Fast (default) | None | Keyword-density ranking | Faster, lightweight |

Smart Mode requires local model weights to be available. If the Smart Mode dependencies (`sentence-transformers`, `torch`, `numpy`) are missing, Strainer automatically falls back to Fast Mode.

---

## Installation

Requires Python 3.

Fast mode (default, no extra dependencies):

```bash
python Strainer.py --help
```

Optional (Smart Mode):

```bash
pip install -r requirements.txt
```

Runs without optional dependencies.

---

## Compatibility

Supported Python versions:

- 3.8
- 3.9
- 3.10
- 3.11
- 3.12

---

## Quick Start

Minimal example:

```bash
echo "We observed three colonies near the edge of the meadow." > my_notes.md
python Strainer.py my_notes.md
```

Expected output format (JSON):

```json
{
  "summary": "We observed three colonies near the edge of the meadow.",
  "tags": ["colonies", "meadow", "honeybee", "field", "observed"],
  "metrics": {
    "original_words": 21,
    "summary_words": 11,
    "compression": "52.4%"
  }
}
```

---

## Usage

CLI:

```bash
python Strainer.py my_notes.md
```

### Options

- `--include-anchors`: Include evidence anchors for summaries and tags in the output.
- `--output-md [path]`: Emit Obsidian-friendly Markdown instead of JSON. If `path` is provided (and does not start with `-`), Strainer writes the Markdown file *and* prints the same Markdown to stdout. If no path is provided, Markdown is printed to stdout only.
- `STRAINER_INCLUDE_ANCHORS`: Environment variable that enables evidence anchors (any non-empty value). Note that there is no CLI flag to disable anchors once this env var is set.

### Examples

Include evidence anchors:

```bash
python Strainer.py my_notes.md --include-anchors
```

Enable evidence anchors via environment variable:

```bash
STRAINER_INCLUDE_ANCHORS=1 python Strainer.py my_notes.md
```

Emit Markdown (Obsidian-friendly) instead of JSON:

```bash
python Strainer.py my_notes.md --output-md
```

Write Markdown to a file:

```bash
python Strainer.py my_notes.md --output-md summary.md
```

Pipe input:

```bash
cat article.txt | python Strainer.py -
```

Drag & drop (Windows):

1. Keep Strainer.py and Drag_Text_Here.bat in the same folder.
2. Drag a .txt or .md file onto Drag_Text_Here.bat.
3. Read JSON output in the console.

---

## Example output (JSON)

```json
{
  "summary": "We observed three colonies near the edge of the meadow.",
  "tags": ["colonies", "meadow", "honeybee", "field", "observed"],
  "metrics": {
    "original_words": 21,
    "summary_words": 11,
    "compression": "52.4%"
  }
}
```

Optional evidence anchors:

```json
{
  "evidence": {
    "summary": [
      {
        "sentence": "We observed three colonies near the edge of the meadow.",
        "source_index": 0,
        "start": 0,
        "end": 48
      }
    ],
    "tags": [
      { "tag": "colonies", "position": 0 }
    ]
  }
}
```

---

## Markdown cleaning

Before analysis, Strainer removes common Markdown noise:

- Frontmatter
- Links
- Images
- Formatting artifacts

This keeps tags and summaries focused on content, not syntax.

---

## License

MIT License. See [LICENSE](LICENSE).
