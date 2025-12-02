# FleaHive 🐝

**A drag-and-drop local summarizer & tagger.**
100% Offline. Zero Cloud. Instant Results.

## What is this?
FleaHive is a "Micro-Tool" designed for friction-free text analysis. It accepts `.txt` or `.md` (Markdown) files and instantly returns a JSON object containing:
- An extractive summary (using semantic ranking or keyword density).
- Auto-generated tags (topics).
- Word count metrics.

It is designed to be a **"Flea"**—a tiny, hyper-specialized worker script that lives in your toolbox, not a bloated SaaS subscription.

## Features
- **Smart Mode:** Uses `sentence-transformers` (local AI) to understand context and rank sentences by importance.
- **Fast Mode:** If no AI libraries are found, it falls back to a robust keyword density algorithm.
- **Markdown Ready:** Intelligently strips Markdown formatting (links, frontmatter, headers) before analyzing, making it perfect for Obsidian vaults.
- **Drag & Drop:** Includes a Windows Batch wrapper for zero-touch execution.

## Installation

1. Install [Python 3](https://www.python.org/).
2. (Optional) Install the brain for "Smart Mode":
   ```bash
   pip install sentence-transformers