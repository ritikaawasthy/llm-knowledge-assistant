import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UploadSerializer, AskSerializer
from .models import Document, Chunk, QAInteraction
from .utils.pdf_ingest import extract_text_from_pdf
from .utils.chunking import chunk_text
from .utils.embeddings import get_openai_embeddings, get_local_embeddings
from .utils.faiss_store import load_index, create_index, add_embeddings, search
from .utils.prompt_builder import build_prompt
import numpy as np
import openai
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY

class UploadView(APIView):
    permission_classes = [permissions.AllowAny]  # change in prod
    def post(self, request):
        s = UploadSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        file = s.validated_data["file"]
        title = s.validated_data.get("title") or file.name
        # Save Document record
        doc = Document.objects.create(title=title, filename=file.name)
        # save file locally
        path = f"/tmp/{file.name}"
        with open(path, "wb") as f:
            for chunk in file.chunks():
                f.write(chunk)
        pages = extract_text_from_pdf(path)
        # chunk pages and create Chunk models
        all_texts = []
        metadatas = []
        for p in pages:
            page_num = p["page_number"]
            if not p["text"].strip():
                continue
            chunks = chunk_text(p["text"], chunk_size=1200, overlap=200)
            for c in chunks:
                Chunk.objects.create(document=doc, text=c["text"], page_number=page_num, chunk_id=c["id"])
                all_texts.append(c["text"])
                metadatas.append({
                    "chunk_id": c["id"],
                    "document_title": doc.title,
                    "page_number": page_num
                })
        # create embeddings and store in FAISS
        try:
            embeddings = get_openai_embeddings(all_texts)
        except Exception as e:
            embeddings = get_local_embeddings(all_texts)
        # load or create index
        index, meta = load_index()
        dim = len(embeddings[0])
        if index is None:
            index = create_index(dim)
            meta = []
        add_embeddings(index, meta, [np.array(e, dtype="float32") for e in embeddings], metadatas)
        return Response({"status": "ok", "document_id": doc.id})

class AskQuestionView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        s = AskSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        question = s.validated_data["question"]
        top_k = s.validated_data["top_k"]
        # get embedding of question
        try:
            q_emb = get_openai_embeddings([question])[0]
        except Exception:
            q_emb = get_local_embeddings([question])[0]
        index, meta = load_index()
        if index is None:
            return Response({"error": "Knowledge base empty"}, status=400)
        results = search(index, meta, q_emb, top_k=top_k)
        # Build prompt using retrieved chunks
        retrieved = []
        for r in results:
            retrieved.append({
                "text": r.get("text") if "text" in r else Chunk.objects.filter(chunk_id=r["chunk_id"]).first().text,
                "document_title": r.get("document_title"),
                "page_number": r.get("page_number")
            })
        prompt = build_prompt(question, retrieved)
        # call LLM - use ChatCompletion for better conversational replies
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # or gpt-4o, or gpt-4 if available; use a capable model available to you
            messages=[{"role":"system", "content":"You are an assistant that answers using context only."},
                      {"role":"user", "content": prompt}],
            max_tokens=500,
            temperature=0.0,
        )
        answer = completion["choices"][0]["message"]["content"].strip()
        # construct sources list
        sources = []
        for i, r in enumerate(retrieved, start=1):
            sources.append(f"{r['document_title']} - Page {r['page_number']}")
        # log interaction
        QAInteraction.objects.create(question=question, answer=answer, sources=sources, meta={"retrieved_count": len(retrieved)})
        return Response({"answer": answer, "sources": sources})
