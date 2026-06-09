"""
embed.py — Milestone 4: Embedding + Vector Store
RAG Pipeline: The Unofficial GPU/CPU Guide

Pipeline stage: Chunks → Embedding (all-MiniLM-L6-v2) → ChromaDB

Reads chunks produced by ingest.py, embeds them with sentence-transformers,
and persists them in a local ChromaDB collection with source metadata.
Also exposes a retrieve() function used by generate.py.
"""

import os
from dotenv import load_dotenv
load_dotenv()  # load .env before any os.environ.get() calls

import chromadb
from sentence_transformers import SentenceTransformer
from ingest import build_chunks, SOURCES

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

COLLECTION_NAME = "gpu_cpu_guide"
CHROMA_PATH     = "./chroma_db"        # persisted to disk
EMBED_MODEL     = "all-MiniLM-L6-v2"
TOP_K           = 5
CHUNK_SIZE      = 500
OVERLAP         = 50

# ---------------------------------------------------------------------------
# Build or load the ChromaDB collection
# ---------------------------------------------------------------------------

def get_collection(rebuild: bool = False):
    """
    Return a ChromaDB collection.
    If rebuild=True (or the collection doesn't exist), fetch all sources,
    embed every chunk, and persist to disk.
    Otherwise, load the existing persisted collection.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Check whether the collection already exists and has data
    existing = [c.name for c in client.list_collections()]
    already_built = COLLECTION_NAME in existing

    if already_built and not rebuild:
        collection = client.get_collection(COLLECTION_NAME)
        print(f"[embed] Loaded existing collection '{COLLECTION_NAME}' "
              f"({collection.count()} chunks).")
        return collection

    # --- Build from scratch ---
    if already_built:
        client.delete_collection(COLLECTION_NAME)
        print(f"[embed] Deleted old collection '{COLLECTION_NAME}' for rebuild.")

    collection = client.create_collection(COLLECTION_NAME)
    print(f"[embed] Created new collection '{COLLECTION_NAME}'.")

    # 1. Ingest
    print("\n[embed] Running ingestion pipeline...")
    chunks = build_chunks(SOURCES, chunk_size=CHUNK_SIZE, overlap=OVERLAP)
    if not chunks:
        raise RuntimeError("Ingestion returned 0 chunks — check ingest.py output.")
    print(f"[embed] {len(chunks)} chunks ready for embedding.")

    # 2. Embed
    print(f"\n[embed] Loading embedding model '{EMBED_MODEL}'...")
    model = SentenceTransformer(EMBED_MODEL)

    texts = [c["text"] for c in chunks]
    print(f"[embed] Embedding {len(texts)} chunks (this may take a minute)...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)

    # 3. Store in ChromaDB
    # IDs must be unique strings; we use "sourcename_chunkid"
    ids       = [f"{c['source']}_{c['chunk_id']}" for c in chunks]
    metadatas = [{"source": c["source"], "url": c["url"], "chunk_id": c["chunk_id"]}
                 for c in chunks]

    # ChromaDB add() accepts lists; embeddings must be plain Python lists
    collection.add(
        ids        = ids,
        embeddings = embeddings.tolist(),
        documents  = texts,
        metadatas  = metadatas,
    )

    print(f"[embed] Stored {collection.count()} chunks in ChromaDB at '{CHROMA_PATH}'.")
    return collection


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

_model_cache: SentenceTransformer | None = None

def _get_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it."""
    global _model_cache
    if _model_cache is None:
        _model_cache = SentenceTransformer(EMBED_MODEL)
    return _model_cache


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """
    Embed a query and return the top-k most relevant chunks.

    Returns a list of dicts:
        {
            "text":     str,   # chunk content
            "source":   str,   # source name key
            "url":      str,   # original URL
            "distance": float, # lower = more relevant (cosine distance)
        }
    """
    model      = _get_model()
    collection = get_collection()

    query_embedding = model.encode([query])[0].tolist()

    results = collection.query(
        query_embeddings = [query_embedding],
        n_results        = k,
        include          = ["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text":     text,
            "source":   meta["source"],
            "url":      meta["url"],
            "distance": round(dist, 4),
        })

    return chunks


# ---------------------------------------------------------------------------
# Retrieval test — run this directly to validate before wiring generation
# ---------------------------------------------------------------------------

TEST_QUERIES = [
    "What GPU should I buy for AAA gaming at 1440p?",
    "How does a CPU affect gaming performance?",
    "What is the difference between a CPU and GPU?",
]

if __name__ == "__main__":
    import sys

    rebuild_flag = "--rebuild" in sys.argv
    get_collection(rebuild=rebuild_flag)

    print("\n" + "=" * 60)
    print("RETRIEVAL TEST — 3 evaluation queries")
    print("=" * 60)

    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        print("-" * 50)
        hits = retrieve(query)
        for i, hit in enumerate(hits, 1):
            print(f"  [{i}] source={hit['source']}  distance={hit['distance']}")
            print(f"       {hit['text'][:200]}...")

    print("\n[OK] Retrieval test complete.")
    print("Check: distances on top results should be below 0.5.")
    print("Check: returned chunks should visibly relate to each query.")