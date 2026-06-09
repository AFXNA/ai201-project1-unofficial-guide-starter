# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

My domain is about choosing the right GPU and CPU based on different factors such as power, performance, power-to-performance ratio. For instance, if someone would like to play AAA game and have little to no knowledge, the individual will have a hard time finding the right component for his/her PC. 

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Lenovo | A web article | https://www.lenovo.com/us/en/glossary/what-is-graphics-card/ |
| 2 | PC Gamer| A web article | https://www.pcgamer.com/the-best-graphics-cards/ |
| 3 | IBM | A web article | https://www.ibm.com/think/topics/gpu |
| 4 | CaseGuard | A web article | https://caseguard.com/articles/graphics-cards-why-choosing-the-right-one-matters/ |
| 5 | IBM | A web article | https://www.ibm.com/think/topics/central-processing-unit |
| 6 | Solarwinds | A web article | https://www.solarwinds.com/resources/it-glossary/what-is-cpu |
| 7 | Tom's Hardware | A Web Article | https://www.tomshardware.com/reviews/best-cpus,3986.html |
| 8 | Intel | A web article | https://www.intel.com/content/www/us/en/gaming/resources/how-cpus-affect-your-gaming-experience.html |
| 9 | Intel | A web article | https://www.intel.com/content/www/us/en/products/docs/processors/cpu-vs-gpu.html |
| 10 | AMD | A web article | https://www.amd.com/en/blogs/2025/why-your-host-cpu-matters-more-than-you-think--ma.html |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
 600 - 800
**Overlap:**
 100 - 200
**Reasoning:**
 600 - 800 characters are approximately 80-120 words. My documents mainly contain paragraphs about the PC components so 80-120 words as a chunk size is ideal. 
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

I am choosing sentence-transformers/all-MiniLM-L6-v2 because it is free, lightweight, fast, and widely used for semantic search applications.

**Top-k:**

k = 5. This provides enough context from multiple sources while minimizing irrelevant information sent to the LLM.

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What GPU should I buy for AAA gaming at 1440p? | A mid-to-high-end GPU such as an AMD Radeon RX 9070 XT or NVIDIA RTX 5070 Ti depending on budget and performance goals.|
| 2 | How does a CPU affect gaming performance? | The CPU processes game logic, AI, physics, and instructions while the GPU renders graphics. A weak CPU can bottleneck a powerful GPU.|
| 3 | What is the difference between a CPU and GPU? | CPUs handle general-purpose sequential tasks while GPUs excel at highly parallel computations and graphics rendering.|
| 4 | Is power consumption important when choosing a GPU? | Yes. Higher power consumption increases electricity usage, cooling requirements, and PSU requirements. Power-to-performance ratio should be considered. |
| 5 | What CPU is recommended for gaming and productivity? |  CPUs such as AMD Ryzen 7 9800X3D or Intel Core Ultra 7 provide strong gaming and multitasking performance.|

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. The user can ask vague question that can affect the anticipated answer. Without any specifications, the retrieval may fail to bring concise answer. 

2. Chunking boundary issue. Since we are using fixed-size chunking, some important information may be way out of the boundary. 

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

     Document Ingestion ---> Chunking (600-800 chars a chunk, 80-100 overlap) 
     ---> Embed (all-MiniLM-L6-v2 ) ---> Store (ChromaDB) ---> Retrieval (k = 5)
     ---> Response generation (Groq Llama)

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

     I will input this markdown file to claude to help me implement functions such as ingesting the fixed-size chunks, answer generation, and so on. In terms of coding, I will use Claude AI to implement the functions while I give the constraints and directions based on the requirements. 

**Milestone 3 — Ingestion and chunking:**
Created ingest.py

**Milestone 4 — Embedding and retrieval:**
Created embed.py
**Milestone 5 — Generation and interface:**
Created generate.py