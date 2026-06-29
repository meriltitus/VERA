from typing import Dict, Any

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

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
- Explain like you're talking to a smart friend, not writing a textbook.
- Use simple everyday language and analogies where helpful.
- Never copy sentences directly from the source — always rephrase in your own words.
- Be concise. One clear answer, no filler phrases.
- If the answer is not in the context, say exactly: "I could not find this in the uploaded documents."
- Do NOT use your own knowledge outside the context.

Context:
{context}

Question: {question}

Answer:"""
    ),
    "conceptual": PromptTemplate(
        input_variables=["context", "question"],
        template="""You are VERA, a document assistant. Explain the concept clearly using ONLY the context provided below.

STRICT RULES:
- Explain this like you're teaching a friend who is smart but new to the topic.
- Use analogies and real-world comparisons to make it click.
- Never copy sentences from the source — always rephrase naturally.
- Break it into short, clear paragraphs. No bullet points unless it genuinely helps.
- Use ONLY information from the context. If it's not there, say: "The uploaded documents don't fully cover this."
- Do NOT add outside knowledge.

Context:
{context}

Question: {question}

Explanation:"""
    ),
    "summary": PromptTemplate(
        input_variables=["context", "question"],
        template="""You are VERA, a document assistant. Summarize the content using ONLY the context provided below.

STRICT RULES:
- Write this like a helpful overview a friend would give after reading the document.
- Use plain language. Avoid jargon unless you explain it immediately after.
- Never copy sentences from the source — rephrase everything naturally.
- Keep it structured but readable — short paragraphs or light bullet points.
- Summarize ONLY what is in the context. Do NOT add outside knowledge.

Context:
{context}

Request: {question}

Summary:"""
    ),
}

PROMPTS["devils_advocate"] = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are VERA, a warm but challenging tutor. Your job is to test the user's understanding using the documents provided.

STRICT RULES:
- Use ONLY the context below. Never invent facts.
- Ask ONE question at a time. Never fire multiple questions.- NEVER mention "Source 1", "Source 2", or any source numbers in your questions. Ask naturally as if you already know the material.
- If the user's answer is CORRECT: affirm them warmly in one sentence, then go one level deeper with a follow-up question.
- If the user's answer is WRONG or INCOMPLETE:
    1. First, kindly explain what the correct answer actually is using plain language and an analogy if helpful.
    2. Make sure they understand before moving on.
    3. Then ask a related follow-up to confirm they've got it.
- If the user says they don't understand or asks for clarification: explain the concept again differently, using a simpler analogy.
- Keep your tone encouraging, like a good teacher who wants the student to succeed.
- Never just cite the source — always explain what it means in plain words first.
- Keep responses concise but complete. No one-liners, no essays.

Context:
{context}

User's response: {question}

Your response:"""
)

def synthesize(router_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes router output, builds a prompt, calls Llama 3, returns a clean answer.
    """
    query = router_output["query"]
    query_type = router_output["query_type"]
    chunks = router_output["chunks"]

    log.info(f"Synthesizing answer for query_type='{query_type}' using {len(chunks)} chunks")

    if not chunks:
        return {
            "query": query,
            "query_type": query_type,
            "answer": "I could not find anything related to this in your uploaded documents. Please ask something covered in the material.",
            "citations": [],
            "chunks_used": 0,
        }

    context = build_context_block(chunks)
    citations = build_citations(chunks)

    prompt_template = PROMPTS.get(query_type, PROMPTS["conceptual"])
    prompt = prompt_template.format(context=context, question=query)

    llm = OllamaLLM(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0.1,
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


def synthesize_stream(router_output: Dict[str, Any]):
    """
    Yields tokens in real-time alongside citations metadata.
    """
    query = router_output["query"]
    query_type = router_output["query_type"]
    chunks = router_output["chunks"]

    if not chunks:
        yield {
            "type": "meta",
            "query": query,
            "query_type": query_type,
            "citations": [],
            "chunks_used": 0,
        }
        yield {"type": "token", "content": "I could not find anything related to this in your uploaded documents. Please ask something covered in the material."}
        return

    context = build_context_block(chunks)
    citations = build_citations(chunks)

    yield {
        "type": "meta",
        "query": query,
        "query_type": query_type,
        "citations": citations,
        "chunks_used": len(chunks),
    }

    prompt_template = PROMPTS.get(query_type, PROMPTS["conceptual"])
    prompt = prompt_template.format(context=context, question=query)

    llm = OllamaLLM(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0.1,
        num_predict=512,
    )

    for chunk in llm.stream(prompt):
        yield {"type": "token", "content": chunk}

