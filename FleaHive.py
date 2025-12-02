#!/usr/bin/env python3
# FleaHive — Best local paper / notes / book summarizer 2025
# Drag any .txt onto this file → instant summary + tags + stats
# 100% offline · zero accounts · zero cost

import re, sys, json
from collections import Counter

# Optional brain upgrade (pip install sentence-transformers once)
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
except:
    model = None

def clean(text):
    # 1. Remove Frontmatter (metadata at top of .md files)
    text = re.sub(r'(?m)^---[\s\S]+?---', '', text)
    
    # 2. Fix Markdown Links: [Text](URL) -> Text
    # This keeps "Text" and deletes the URL parts
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # 3. Remove standard noise (Refs, URLs, Images)
    text = re.sub(r'(?i)@article{[^}]+}|https?://\S+|doi:\S+', '', text)
    text = re.sub(r'!\[.*?\]\([^\)]+\)', '', text) # Remove images completely
    
    # 4. Remove Markdown formatting symbols (*, #, >, `)
    text = re.sub(r'[*#>`~]', '', text) 
    
    # 5. Clean up structural noise
    text = re.sub(r'^Table\s*\d+.*|^Figure\s*\d+.*', '', text, flags=re.M|re.I)
    
    # 6. Cut off references section if present
    cutoff = re.search(r'(?i)\n\s*(references|bibliography|appendix)\s*\n', text)
    if cutoff: text = text[:cutoff.start()]
    
    return text.strip()

def summarize(text, max_len=450):
    text = clean(text)
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 20]
    if not sentences:
        return "Nothing to summarize after cleaning."

    if model:  # semantic mode — compares every sentence to the whole document
        embeddings = model.encode([text] + sentences)
        doc_vec = embeddings[0]
        scores = [float(doc_vec @ emb) for emb in embeddings[1:]]
        ranked = sorted(zip(scores, sentences), reverse=True)
    else:  # pure keyword mode (still excellent)
        words = re.findall(r'\w+', text.lower())
        common = {w for w, c in Counter(words).most_common(20) if len(w) > 4}
        ranked = sorted([(sum(w[:5] in s.lower() for w in common), s) for s in sentences], reverse=True)

    result, used = [], 0
    for _, s in ranked:
        if used + len(s) <= max_len:
            result.append(s)
            used += len(s)
        else:
            break
    return " ".join(result) or text[:max_len] + "…"

def tag(text, top=8):
    words = re.findall(r'\w+', text.lower())
    stop = {
        'the','and','for','with','this','that','from','were','been','have','using','used',
        'which','their','they','will','would','there','these','about','when','what','where',
        'is','are','was','not','but','all','into','can','has','more','one','its','out',
        'also','than','other','some','very','only','time','just','even','most','like','may',
        'such','each','new','based','our','results','study','method','approach','proposed'
    }
    candidates = [w for w in words if w not in stop and len(w) > 3]
    candidates = [w for w in words if w not in stop and len(w) > 3]
    return [w for w, _ in Counter(candidates).most_common(top)]

# ——————— RUN ———————
if len(sys.argv) < 2:
    print(json.dumps({"error": "Drag a .txt file here or pipe text in"}))
    sys.exit(1)

path = sys.argv[1]
try:
    text = sys.stdin.read() if path == '-' else open(path, 'r', encoding='utf-8').read()
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)

summary = summarize(text)
tags = tag(summary + text)

result = {
    "summary": summary,
    "tags": tags,
    "metrics": {
        "original_words": len(re.findall(r'\w+', text)),
        "summary_words": len(re.findall(r'\w+', summary)),
        "compression": f"{len(summary)/max(len(text),1):.1%}"
    }
}

print(json.dumps(result, indent=2, ensure_ascii=False))