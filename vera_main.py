from typing import Dict

from router.query_handler import handle_query
from aggregator.synthesizer import synthesize
from utils.logger import get_logger

log = get_logger(__name__)


def ask_vera(question: str, collection_name: str = "vera_docs", mode: str = "Researcher", chat_history: list = None) -> Dict:
    log.info(f"VERA received question: '{question}' | mode: {mode}")

    # Build context-aware question if there's chat history
    if chat_history and len(chat_history) >= 2:
        # Take last 3 exchanges max to avoid bloating the prompt
        recent = chat_history[-6:]
        history_text = ""
        for msg in recent:
            if msg["role"] == "user":
                history_text += f"User: {msg['content']['text']}\n"
            elif msg["role"] == "vera":
                history_text += f"VERA: {msg['content'].get('answer', '')[:200]}\n"
        # Rewrite the question with history context for better retrieval
        contextual_question = f"{history_text}User follow-up: {question}"
    else:
        contextual_question = question

    router_output = handle_query(contextual_question, collection_name=collection_name)
    router_output["original_question"] = question  # keep original for display

    if mode == "Devil's Advocate":
        router_output["query_type"] = "devils_advocate"

    result = synthesize(router_output)
    return result


def print_answer(result: dict):
    """Pretty-prints the final VERA answer to the terminal."""
    print("\n" + "="*60)
    print(f"🔍 Query ({result['query_type'].upper()}): {result['query']}")
    print("="*60)
    print(f"\n📖 Answer:\n\n{result['answer']}")
    print(f"\n📌 Sources ({result['chunks_used']} chunks used):")
    for citation in result["citations"]:
        print(f"   {citation}")
    print("="*60 + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m vera_main \"your question here\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    result = ask_vera(question)
    print_answer(result)
