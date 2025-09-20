PROMPT_TEMPLATE = """
You are a helpful assistant answering user questions using ONLY the context provided.
If the answer is not contained in the context, say "I don't know based on the provided documents."
Do not invent facts.

Context:
{context}

Question:
{question}

Answer concisely and cite the source(s) used (format: Document Title - Page X).
"""

def build_prompt(question, retrieved_chunks):
    # retrieved_chunks: list of dicts with keys: text, document_title, page_number
    context_parts = []
    for i, c in enumerate(retrieved_chunks, start=1):
        header = f"[{i}] {c.get('document_title','Document')} - Page {c.get('page_number','?')}\n"
        context_parts.append(header + c['text'])
    context = "\n\n---\n\n".join(context_parts)
    return PROMPT_TEMPLATE.format(context=context, question=question)
