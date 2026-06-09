"""
generate.py — Milestone 5: Retrieval-Grounded Generation
RAG Pipeline: The Unofficial GPU/CPU Guide

Pipeline stage: Query → Retrieval → Prompt → Groq Llama → Grounded Answer

Pulls the top-k chunks from embed.py and passes them as context to
Groq's llama-3.3-70b-versatile. The system prompt enforces that the
model answers ONLY from the retrieved context — not from training knowledge.
Source URLs are appended programmatically so attribution is guaranteed.
"""

import os
from dotenv import load_dotenv
load_dotenv()  # must run before any os.environ.get() calls

from groq import Groq
from embed import retrieve

# ---------------------------------------------------------------------------
# Groq client — reads GROQ_API_KEY from environment / .env
# ---------------------------------------------------------------------------

def _get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY not found. "
            "Add it to a .env file or export it in your shell:\n"
            "  export GROQ_API_KEY=your_key_here"
        )
    return Groq(api_key=api_key)


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a helpful PC hardware advisor for people who want to choose the right GPU or CPU.

Answer the user's question using ONLY the information provided in the CONTEXT section below.
- If the context contains a clear answer, give a specific, helpful response.
- If the context does not contain enough information to answer the question, say exactly:
  "I don't have enough information in my sources to answer that."
- Do NOT use your general training knowledge about hardware.
- Do NOT make up product names, benchmarks, or specifications.
- Keep your answer concise and practical (3–6 sentences is ideal).
- Do not mention that you are using retrieved context or documents in your answer."""


def _build_user_message(query: str, chunks: list[dict]) -> str:
    """Format retrieved chunks as numbered context blocks + the user's question."""
    context_blocks = []
    for i, chunk in enumerate(chunks, 1):
        context_blocks.append(
            f"[{i}] (source: {chunk['source']})\n{chunk['text']}"
        )
    context = "\n\n".join(context_blocks)

    return f"""CONTEXT:
{context}

QUESTION:
{query}"""


# ---------------------------------------------------------------------------
# Main ask() function — called by app.py
# ---------------------------------------------------------------------------

def ask(query: str, k: int = 5) -> dict:
    """
    Run the full RAG pipeline for a single query.

    Returns:
        {
            "answer":  str,        # grounded LLM response
            "sources": list[str],  # deduplicated source URLs used
            "chunks":  list[dict], # raw retrieved chunks (for debugging)
        }
    """
    # 1. Retrieve relevant chunks
    chunks = retrieve(query, k=k)

    # 2. Build prompt
    user_message = _build_user_message(query, chunks)

    # 3. Call Groq
    client   = _get_client()
    response = client.chat.completions.create(
        model    = "llama-3.3-70b-versatile",
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature = 0.2,   # low temperature for factual, consistent answers
        max_tokens  = 512,
    )

    answer = response.choices[0].message.content.strip()

    # 4. Programmatic source attribution — deduplicated, ordered by relevance
    seen = set()
    sources = []
    for chunk in chunks:
        if chunk["url"] not in seen:
            seen.add(chunk["url"])
            sources.append(chunk["url"])

    return {
        "answer":  answer,
        "sources": sources,
        "chunks":  chunks,
    }


# ---------------------------------------------------------------------------
# Quick CLI test — run directly to validate end-to-end before launching UI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    TEST_QUERIES = [
        # Should answer from context
        "What GPU should I buy for AAA gaming at 1440p?",
        "What is the difference between a CPU and GPU?",
        # Should trigger "not enough information" response
        "What is the best mechanical keyboard for gaming?",
    ]

    print("=" * 60)
    print("END-TO-END GENERATION TEST")
    print("=" * 60)

    for query in TEST_QUERIES:
        print(f"\nQ: {query}")
        print("-" * 50)
        result = ask(query)
        print(f"A: {result['answer']}")
        print(f"\nSources ({len(result['sources'])}):")
        for url in result['sources']:
            print(f"  • {url}")
        print()

    print("[OK] Generation test complete.")
    print("Verify: in-domain answers should cite real sources.")
    print("Verify: the keyboard question should say 'not enough information'.")