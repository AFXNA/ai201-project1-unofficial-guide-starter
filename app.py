"""
app.py — Milestone 5: Gradio Interface
RAG Pipeline: The Unofficial GPU/CPU Guide
"""

import os
from dotenv import load_dotenv
import gradio as gr
from generate import ask

# Load GROQ_API_KEY from .env if present
load_dotenv()

# ---------------------------------------------------------------------------
# Example questions shown in the UI
# ---------------------------------------------------------------------------

EXAMPLES = [
    "What GPU should I buy for AAA gaming at 1440p?",
    "How does a CPU affect gaming performance?",
    "What is the difference between a CPU and GPU?",
    "Is power consumption important when choosing a GPU?",
    "What CPU is recommended for gaming and productivity?",
]

# ---------------------------------------------------------------------------
# Handler — called on every query
# ---------------------------------------------------------------------------

def handle_query(question: str):
    """
    Run the RAG pipeline and return (answer, sources_text) for Gradio outputs.
    """
    question = question.strip()
    if not question:
        return "Please enter a question.", ""

    try:
        result = ask(question)
    except EnvironmentError as e:
        return str(e), ""
    except Exception as e:
        return f"An error occurred: {e}", ""

    answer = result["answer"]

    # Format sources as a numbered list
    if result["sources"]:
        sources_text = "\n".join(
            f"{i}. {url}" for i, url in enumerate(result["sources"], 1)
        )
    else:
        sources_text = "No sources retrieved."

    return answer, sources_text


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

with gr.Blocks(title="The Unofficial GPU/CPU Guide") as demo:

    gr.Markdown(
        """
        # 🖥️ The Unofficial GPU/CPU Guide
        Ask a question about choosing a GPU or CPU for gaming or productivity.
        Answers are grounded in the 10 source documents from your RAG pipeline —
        the system will say so if it can't find the answer in its sources.
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            question_box = gr.Textbox(
                label       = "Your question",
                placeholder = "e.g. What GPU should I buy for 1440p gaming?",
                lines       = 2,
            )
            with gr.Row():
                submit_btn = gr.Button("Ask", variant="primary")
                clear_btn  = gr.Button("Clear")

        with gr.Column(scale=1):
            gr.Markdown("**Example questions**")
            for example in EXAMPLES:
                gr.Button(example, size="sm").click(
                    fn      = lambda q=example: q,
                    outputs = question_box,
                )

    answer_box = gr.Textbox(
        label      = "Answer",
        lines      = 8,
        interactive= False,
    )

    sources_box = gr.Textbox(
        label      = "Retrieved from",
        lines      = 5,
        interactive= False,
    )

    # Wire up submit
    submit_btn.click(
        fn      = handle_query,
        inputs  = question_box,
        outputs = [answer_box, sources_box],
    )

    # Also submit on Enter
    question_box.submit(
        fn      = handle_query,
        inputs  = question_box,
        outputs = [answer_box, sources_box],
    )

    # Clear button resets all fields
    clear_btn.click(
        fn      = lambda: ("", "", ""),
        outputs = [question_box, answer_box, sources_box],
    )

    gr.Markdown(
        """
        ---
        *Answers are generated from retrieved source documents only.
        If the system lacks sufficient information, it will say so rather than guessing.*
        """
    )

if __name__ == "__main__":
    demo.launch(share=True)