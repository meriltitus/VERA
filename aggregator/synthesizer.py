from typing import Dict, Any

from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

from aggregator.citation_mapper import build_context_block, build_citations
from utils.config import get_settings
from utils.logger import get_logger

log = get_logger(__name__)
settings = get_settings()


# Strict prompts — VERA only answers from provided context
PROMPTS = {
    "factual": PromptTemplate(
        input_variables=["context", "question"],
        template="""You are VERA, a precise document assistant. Your ONLY job is to answer questions using the context provided below.

STRICT RULES:
- Answer ONLY using information from the context below.
- If the answer is not found in the context, respond exactly with: "I could not find information about this in the uploaded documents."
- Do NOT use your own knowledge or make up information.
- Be concise and direct.
- Do not say "based on the context" or "according to the sources" — just answer directly.

Context:
{context}

Question: {question}

Answer:"""
    ),
    "conceptual": PromptTemplate(
        input_variables=["context", "question"],
        template="""You are VERA, a document assistant. Explain the concept clearly using ONLY the context provided below.

STRICT RULES:
- Use ONLY information from the context below.
- If the context does not contain enough information, say: "The uploaded documents do not fully cover this topic."
- Break down the explanation into clear points.
- Do NOT use your own knowledge or add information not present in the context.
- Do not say "based on the context" — just explain directly.

Context:
{context}

Question: {question}

Explanation:"""
    ),
    "summary": PromptTemplate(
        input_variables=["context", "question"],
        template="""You are VERA, a document assistant. Summarize the content using ONLY the context provided below.

STRICT RULES:
- Summarize ONLY what is present in the context below.
- Do NOT add outside knowledge.
- Structure your response with clear bullet points or numbered sections.
- If the context is limited, summarize only what is available.

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
        Dict with query, query_type, answer, citations, chunks_used.
    """
    query = router_output["query"]
    query_type = router_output["query_type"]
    chunks = router_output["chunks"]

    log.info(f"Synthesizing answer for query_type='{query_type}' using {len(chunks)} chunks")

    context = build_context_block(chunks)
    citations = build_citations(chunks)

    prompt_template = PROMPTS.get(query_type, PROMPTS["conceptual"])
    prompt = prompt_template.format(context=context, question=query)

    llm = OllamaLLM(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0.1,       # Very low — stay factual, don't improvise
        num_predict=512,
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
