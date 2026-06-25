from typing import Dict

from router.query_handler import handle_query
from aggregator.synthesizer import synthesize
from utils.logger import get_logger

log = get_logger(__name__)


def ask_vera(question: str, collection_name: str = "vera_docs") -> Dict:
    """
    Full VERA pipeline: question → route → retrieve → synthesize → answer.
    """
    log.info(f"VERA received question: '{question}'")

    # Stage 1: Route
    router_output = handle_query(question, collection_name=collection_name)

    # Stage 2: Synthesize
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
