# strainer-cli 🧺  
Offline document summarization and tagging for text and Markdown

**strainer-cli is a local-first command-line tool that turns `.txt` and `.md` files into structured summaries, tags, and metrics — entirely offline.**  
It is built for pipelines, note systems, and agents, not dashboards or web apps.

- **Input:** plain text / Markdown  
- **Output:** JSON (default) or Obsidian-friendly Markdown  
- **Network:** none (no API calls, no uploads)

---

## What problem it solves

Most summarizers assume a web app, cloud processing, and opaque models. That breaks when:

- Notes must stay on disk (privacy, compliance, or paranoia).
- You want outputs that plug into scripts, search, or agents.
- You need repeatable behavior, not a “maybe it summarizes” black box.

**Use strainer-cli when you want:**

- Fast compression of long notes into a usable digest.
- Tags you can feed into search, indexing, or retrieval systems.
- Output that drops cleanly into scripts, vaults, or local agents.
- Offline operation by default.

---

## What strainer-cli produces

For each input file, strainer-cli emits:

- **Extractive summary** – top-ranked sentences from the source.
- **Tags** – topic keywords inferred from the text.
- **Metrics** – word counts and compression ratio.

Optional:

- **Evidence anchors** – mappings from summary sentences and tags back to positions in the cleaned source text.

### Example JSON output

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

With evidence anchors:

```json
{
  "summary": "We observed three colonies near the edge of the meadow.",
  "tags": ["colonies", "meadow", "honeybee", "field", "observed"],
  "metrics": {
    "original_words": 21,
    "summary_words": 11,
    "compression": "52.4%"
  },
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

## How it works

strainer-cli supports two modes. The output format is the same for both.

| Mode  | Dependencies                              | Ranking approach              | Speed                  |
| ----- | ----------------------------------------- | ----------------------------- | ---------------------- |
| Smart | `sentence-transformers`, `torch`, `numpy` | Embedding-based sentence rank | Slower, higher quality |
| Fast  | None                                      | Keyword-density ranking       | Faster, lightweight    |

* **Fast mode** is the default and requires only Python.
* **Smart mode** uses local sentence embeddings for higher-quality ranking.
  If Smart dependencies are missing, strainer-cli automatically falls back to Fast mode.

Before analysis, Strainer removes common Markdown noise:

* Frontmatter
* Links
* Images
* Formatting artifacts

This keeps summaries and tags focused on content, not syntax.

---

## Installation

Requires **Python 3.8–3.12**.

### Fast mode (default, no extra dependencies)

```bash
python Strainer.py --help
```

### Smart mode (optional)

```bash
pip install -r requirements.txt
```

If Smart mode dependencies are not available, Strainer runs in Fast mode.

---

## Quick start

Minimal example:

```bash
echo "We observed three colonies near the edge of the meadow." > my_notes.md
python Strainer.py my_notes.md
```

Typical output:

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

## CLI usage

Basic usage:

```bash
python Strainer.py my_notes.md
```

### Options

* `--include-anchors`
  Include evidence anchors for summaries and tags in the output.

* `--output-md [path]`
  Emit Obsidian-friendly Markdown instead of JSON.

  * If `path` is provided (and does not start with `-`), Strainer writes the Markdown file and prints the same Markdown to stdout.
  * If no `path` is provided, Markdown is printed to stdout only.

### Environment variable

* `STRAINER_INCLUDE_ANCHORS`
  Any non-empty value enables evidence anchors.
  Note: there is no CLI flag to disable anchors once this env var is set.

---

## Examples

Include evidence anchors:

```bash
python Strainer.py my_notes.md --include-anchors
```

Enable anchors via environment variable:

```bash
STRAINER_INCLUDE_ANCHORS=1 python Strainer.py my_notes.md
```

Emit Markdown instead of JSON:

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

1. Keep `Strainer.py` and `Drag_Text_Here.bat` in the same folder.
2. Drag a `.txt` or `.md` file onto `Drag_Text_Here.bat`.
3. Read JSON output in the console.

---

## When to use strainer-cli vs an LLM API

Choose **strainer-cli** if:

* Data must not leave the machine.
* You need deterministic, replayable outputs.
* You’re building local agents or pipelines that just need summaries + tags.

Choose an **LLM API** if:

* You need free-form rewriting, style changes, or reasoning.
* Network and vendor lock-in are acceptable.

---

## License

MIT License. See [`LICENSE`](LICENSE).
