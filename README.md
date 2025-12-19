# FleaHive 🐝

**A drag-and-drop local summarizer & tagger.**
Small and powerful—built to stay out of your way while giving you fast, useful output.

FleaHive is an offline-first helper that accepts `.txt` or `.md` (Markdown) files and returns structured JSON containing:
- An extractive summary (semantic ranking when available, keyword density otherwise)
- Auto-generated tags (topics)
- Word count metrics

It is designed to live in your toolbox as a small, single-purpose script—not a hosted service.

## Features
- **Smart Mode:** If `sentence-transformers` is installed, FleaHive uses embeddings to rank sentences by importance.
- **Fast Mode:** When you skip optional AI packages, it runs a pure-Python keyword-density algorithm—no extra downloads required.
- **Markdown ready:** Strips frontmatter, links, and other Markdown noise before summarization and tagging.
- **Drag & drop:** Includes a Windows batch wrapper for zero-touch execution.

## Installation

1) Install [Python 3](https://www.python.org/).
2) (Optional but recommended for Smart Mode) install the language model:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Method A: Drag & Drop (Windows)
1) Keep `FleaHive.py` and `Drag_Text_Here.bat` in the same folder.  
2) Drag any `.txt` or `.md` file onto the `Drag_Text_Here.bat` icon.  
3) View the JSON summary printed in the console window.  

### Method B: Command Line
Run FleaHive directly and pass a file path:

```bash
python FleaHive.py my_notes.md
```

### Method C: Pipe Input
Pipe text to FleaHive by passing `-` as the path:

```bash
cat my_article.txt | python FleaHive.py -
```

## Output format

The script prints a JSON document with a summary, tags, and metrics:

```json
{
  "summary": "Top-ranked sentences from your document…",
  "tags": ["topic1", "topic2"],
  "metrics": {
    "original_words": 1234,
    "summary_words": 180,
    "compression": "14.6%"
  }
}
```

### Example: Clean tags from Markdown input

Input (`notes.md`):

```markdown
# Honeybee field report
We observed three colonies near the edge of the meadow.
See [photos](https://example.com/bee-shots) for details.
```

Command:

```bash
python FleaHive.py notes.md
```

Result (notice the tags are free of link/markdown noise):

```json
{
  "summary": "We observed three colonies near the edge of the meadow.",
  "tags": ["colonies", "meadow", "honeybee", "report", "observed", "field"],
  "metrics": {
    "original_words": 21,
    "summary_words": 11,
    "compression": "52.4%"
  }
}
```

## Notes
- FleaHive is fully offline. No network calls are made.
- If optional dependencies are missing, the tool still runs using Fast Mode.
- Markdown cleaning removes common noise (frontmatter, links, and image markup) before summarization and tagging.
