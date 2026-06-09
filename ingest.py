"""
ingest.py — Milestone 3: Document Ingestion and Chunking
RAG Pipeline: The Unofficial GPU/CPU Guide

Pipeline stage: Document Ingestion → Chunking
  - Reads plain .txt files from the ./docs/ folder
  - Normalises whitespace
  - Splits into fixed-size character chunks with overlap

Chunking spec (from planning.md):
  - Chunk size:  700 characters (~100–115 words)
  - Overlap:     150 characters (~20–25 words)
"""

import os
import re

# ---------------------------------------------------------------------------
# Source registry — filename stem maps to the original URL for attribution
# ---------------------------------------------------------------------------

SOURCES = [
    {"name": "lenovo_gpu_glossary",    "url": "https://www.lenovo.com/us/en/glossary/what-is-graphics-card/"},
    {"name": "pcgamer_best_gpus",      "url": "https://www.pcgamer.com/the-best-graphics-cards/"},
    {"name": "ibm_gpu",                "url": "https://www.ibm.com/think/topics/gpu"},
    {"name": "caseguard_gpu_choice",   "url": "https://caseguard.com/articles/graphics-cards-why-choosing-the-right-one-matters/"},
    {"name": "ibm_cpu",                "url": "https://www.ibm.com/think/topics/central-processing-unit"},
    {"name": "solarwinds_cpu",         "url": "https://www.solarwinds.com/resources/it-glossary/what-is-cpu"},
    {"name": "tomshardware_best_cpus", "url": "https://www.tomshardware.com/reviews/best-cpus,3986.html"},
    {"name": "intel_cpu_gaming",       "url": "https://www.intel.com/content/www/us/en/gaming/resources/how-cpus-affect-your-gaming-experience.html"},
    {"name": "intel_cpu_vs_gpu",       "url": "https://www.intel.com/content/www/us/en/products/docs/processors/cpu-vs-gpu.html"},
    {"name": "amd_cpu_matters",        "url": "https://www.amd.com/en/blogs/2025/why-your-host-cpu-matters-more-than-you-think--ma.html"},
]

DOCS_DIR = "./docs"

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_text(name: str) -> str | None:
    """Read a .txt file from DOCS_DIR. Returns None if the file is missing."""
    path = os.path.join(DOCS_DIR, f"{name}.txt")
    if not os.path.exists(path):
        print(f"  [WARN] File not found: {path} — skipping.")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Normalise whitespace in plain text.
    Since the files are already plain text (no HTML), cleaning is minimal:
    collapse runs of spaces/newlines and strip leading/trailing whitespace.
    """
    text = re.sub(r"\r\n|\r", "\n", text)       # normalise line endings
    text = re.sub(r"\n{3,}", "\n\n", text)       # collapse excess blank lines
    text = re.sub(r"[ \t]+", " ", text)          # collapse horizontal whitespace
    return text.strip()

# ---------------------------------------------------------------------------
# Chunk
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """
    Split text into fixed-size character chunks with overlap.

    Args:
        text:       Cleaned plain text string.
        chunk_size: Target size of each chunk in characters (default 700).
        overlap:    Characters repeated at the start of the next chunk (default 150).

    Returns:
        List of non-empty chunk strings.
    """
    if not text:
        return []

    chunks = []
    start = 0
    step  = chunk_size - overlap   # advance 550 chars each iteration

    while start < len(text):
        end   = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks

# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def build_chunks(
    sources: list[dict] = SOURCES,
    chunk_size: int = 700,
    overlap: int = 150,
) -> list[dict]:
    """
    Load, clean, and chunk all source .txt files.

    Returns a list of chunk dicts:
        {
            "text":     str,   # chunk content
            "source":   str,   # source name (matches filename stem)
            "url":      str,   # original URL for attribution
            "chunk_id": int,   # position of chunk within its source doc
        }
    """
    all_chunks = []

    for source in sources:
        name = source["name"]
        url  = source["url"]
        print(f"[{name}] Loading...")

        raw = load_text(name)
        if raw is None:
            continue

        text   = clean_text(raw)
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        print(f"  {len(text):,} chars → {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text":     chunk,
                "source":   name,
                "url":      url,
                "chunk_id": i,
            })

    return all_chunks

# ---------------------------------------------------------------------------
# Inspection helper
# ---------------------------------------------------------------------------

def print_sample_chunks(chunks: list[dict], n: int = 5) -> None:
    """Print n evenly-spaced sample chunks for manual inspection."""
    if not chunks:
        print("No chunks to inspect.")
        return

    step    = max(1, len(chunks) // n)
    indices = list(range(0, len(chunks), step))[:n]

    print("\n" + "=" * 60)
    print(f"SAMPLE CHUNKS ({n} of {len(chunks)} total)")
    print("=" * 60)

    for idx in indices:
        c = chunks[idx]
        print(f"\n[Chunk #{idx}]  source={c['source']}  chunk_id={c['chunk_id']}")
        print(f"  Length : {len(c['text'])} chars")
        print(f"  Preview: {c['text'][:300]}{'...' if len(c['text']) > 300 else ''}")
        print("-" * 60)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    CHUNK_SIZE = 700
    OVERLAP    = 150

    print(f"Starting ingestion — chunk_size={CHUNK_SIZE}, overlap={OVERLAP}\n")

    chunks = build_chunks(chunk_size=CHUNK_SIZE, overlap=OVERLAP)

    print(f"\nTotal chunks : {len(chunks)}")
    print(f"Sources used : {len({c['source'] for c in chunks})}")

    print_sample_chunks(chunks, n=5)

    if len(chunks) < 50:
        print("\n[WARN] Fewer than 50 chunks — some files may be missing or very short.")
    elif len(chunks) > 2000:
        print("\n[WARN] More than 2000 chunks — consider increasing chunk size.")
    else:
        print(f"\n[OK] Chunk count {len(chunks)} is in the healthy range (50–2000).")