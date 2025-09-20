import uuid

def chunk_text(text, chunk_size=1000, overlap=200):
    """
    Chunk text by characters (safe fallback). Returns list of dicts: {"id", "text", "start", "end"}
    """
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk_text = text[start:end]
        chunk_id = str(uuid.uuid4())
        chunks.append({"id": chunk_id, "text": chunk_text, "start": start, "end": end})
        start = end - overlap
        if start < 0:
            start = 0
    return chunks
