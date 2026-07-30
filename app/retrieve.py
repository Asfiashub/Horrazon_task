from sentence_transformers import SentenceTransformer
import numpy as np
from app.ingest import load_all_documents

_model = None
_chunk_embeddings = None
_chunks = None


def _get_model():
    global _model
    if _model is None:
        print("Loading embedding model (first time only)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def build_index():
    """Embed all chunks once and store them in memory."""
    global _chunk_embeddings, _chunks
    model = _get_model()
    _chunks = load_all_documents()
    texts = [c["text"] for c in _chunks]
    print(f"Embedding {len(texts)} chunks...")
    _chunk_embeddings = model.encode(texts, convert_to_numpy=True)
    print("Index built.")


def _cosine_similarity(query_vec, matrix):
    query_norm = query_vec / np.linalg.norm(query_vec)
    matrix_norm = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix_norm @ query_norm


def retrieve(query, doc_type=None, top_k=3):
    """Return top_k most relevant chunks, optionally filtered by doc_type."""
    if _chunk_embeddings is None:
        build_index()

    model = _get_model()
    query_vec = model.encode(query, convert_to_numpy=True)

    candidate_indices = list(range(len(_chunks)))
    if doc_type:
        candidate_indices = [i for i in candidate_indices if _chunks[i]["doc_type"] == doc_type]

    if not candidate_indices:
        return []

    candidate_matrix = _chunk_embeddings[candidate_indices]
    sims = _cosine_similarity(query_vec, candidate_matrix)

    ranked = sorted(zip(candidate_indices, sims), key=lambda x: x[1], reverse=True)
    top = ranked[:top_k]

    results = []
    for idx, score in top:
        results.append({
            "text": _chunks[idx]["text"],
            "doc_type": _chunks[idx]["doc_type"],
            "record_id": _chunks[idx]["record_id"],
            "score": float(score)
        })
    return results


if __name__ == "__main__":
    build_index()
    results = retrieve("Why was the mechanical keyboard refunded?", top_k=5)
    for r in results:
        print(f"[{r['doc_type']} | {r['record_id']} | score={r['score']:.3f}] {r['text']}")