from typing import Dict, Any

from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

from aggregator.citation_mapper import build_context_block, build_citations
from utils.config import get_settings
from utils.logger import get_logger

log = get_logger(__name__)
settings = get_settings()


# Prompt templates per query type
PROMPTS = {
    "factual": PromptTemplate(
        input_variables=["context", "question"],
        template="""You are VERA, a precise knowledge assistant. Answer the question using ONLY the context provided below.
Be direct and factual. If the answer is not in the context, say "I could not find this in the provided documents."

Context:
{context}

Question: {question}

Answer:"""
    ),
    "conceptual": PromptTemplate(
        input_variables=["context", "question"],
        template="""You are VERA, a knowledgeable assistant. Using the context below, provide a clear and thorough explanation.
Break down complex ideas. Use simple language. If the context is insufficient, say so honestly.

Context:
{context}

Question: {question}

Explanation:"""
    ),
    "summary": PromptTemplate(
        input_variables=["context", "question"],
        template="""You are VERA, a summarization assistant. Using the context below, provide a structured summary.
Organize your response with key points. Cover the main topics present in the context.

Context:
{context}

Request: {question}

Summary:"""
    ),
}


def synthesize(router_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes router output, builds a prompt, calls Llama 3, returns a clean answer.

    Args:
        router_output: Output from query_handler.handle_query()

    Returns:
        Dict with:
            - query:        original question
            - query_type:   classified type
            - answer:       LLM generated answer
            - citations:    formatted citation list
            - chunks_used:  number of chunks fed to LLM
    """
    query = router_output["query"]
    query_type = router_output["query_type"]
    chunks = router_output["chunks"]

    log.info(f"Synthesizing answer for query_type='{query_type}' using {len(chunks)} chunks")

    # Build context and citations
    context = build_context_block(chunks)
    citations = build_citations(chunks)

    # Select prompt by query type
    prompt_template = PROMPTS.get(query_type, PROMPTS["conceptual"])
    prompt = prompt_template.format(context=context, question=query)

    # Call Llama 3 via Ollama
    llm = OllamaLLM(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0.2,       # Low temp = focused, factual answers
        num_predict=512,       # Max tokens in response
    )

    log.info("Calling Llama 3 for answer generation...")
    answer = llm.invoke(prompt)

    log.info("Answer generated successfully")

    return {
        "query": query,
        "query_type": query_type,
        "answer": answer.strip(),
        "citations": citations,
        "chunks_used": len(chunks),
    }
