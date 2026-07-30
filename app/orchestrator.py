import os
from dotenv import load_dotenv
from app.retrieve import retrieve
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

load_dotenv()

print("URL:", os.getenv("WATSONX_URL"))
print("KEY (first 6 chars):", os.getenv("GRANITE_API_KEY")[:6] if os.getenv("GRANITE_API_KEY") else "MISSING")
print("PROJECT ID:", os.getenv("WATSONX_PROJECT_ID"))

DOC_TYPES = ["orders", "refunds", "support_tickets"]

_model = None


def _get_llm():
    global _model
    if _model is None:
        credentials = Credentials(
            url=os.getenv("WATSONX_URL"),
            api_key=os.getenv("GRANITE_API_KEY")
        )
        _model = ModelInference(
            model_id="ibm/granite-4-h-small",
            credentials=credentials,
            project_id=os.getenv("WATSONX_PROJECT_ID"),
            params={
                "max_new_tokens": 400,
                "temperature": 0.2
            }
        )
    return _model


def gather_evidence(query, top_k_per_type=2):
    evidence = []
    for doc_type in DOC_TYPES:
        results = retrieve(query, doc_type=doc_type, top_k=top_k_per_type)
        evidence.extend(results)
    return evidence


def build_prompt(query, evidence):
    evidence_text = ""
    for e in evidence:
        evidence_text += f"- [{e['doc_type']} | {e['record_id']}] {e['text']}\n"

    prompt = f"""You are an AI assistant answering business questions for NovaCart Global using ONLY the evidence provided below.

EVIDENCE:
{evidence_text}

QUESTION: {query}

Instructions:
1. Answer using only the evidence above — do not invent facts.
2. Explicitly list which document types and record IDs you used (e.g. "orders/ORD1005, refunds/REF2002").
3. If the evidence is insufficient or conflicting, say so clearly instead of guessing.
4. Keep the answer concise and business-focused.

ANSWER:"""
    return prompt


def answer_question(query):
    evidence = gather_evidence(query)
    prompt = build_prompt(query, evidence)

    llm = _get_llm()
    response = llm.generate_text(prompt=prompt)

    return {
        "question": query,
        "answer": response.strip(),
        "sources": [{"doc_type": e["doc_type"], "record_id": e["record_id"]} for e in evidence]
    }


if __name__ == "__main__":
    result = answer_question("Why was the mechanical keyboard order refunded twice?")
    print("ANSWER:\n", result["answer"])
    print("\nSOURCES:\n", result["sources"])

