# NovaCart Insight Assistant

A small, working **Retrieval-Augmented Generation (RAG)** prototype that answers business questions for **NovaCart Global** by retrieving and reasoning across multiple document types (orders, refunds, and support tickets) while providing evidence-backed source citations for every response.

> Built for **Horrazon AI – Round II Engineering Challenge**  
> **Role:** AI/ML Engineer Intern (LLM & Agentic AI)

---

# Overview

NovaCart's business data is distributed across multiple disconnected sources such as orders, refunds, support tickets, warehouse logs, and supplier reports. Answering a business question like:

> *"Why did refunds increase last month?"*

typically requires manually searching multiple systems and combining information across teams, making the process slow and difficult to verify.

This project demonstrates a **Retrieval-Augmented Generation (RAG)** system that:

- Accepts natural language business questions
- Retrieves relevant evidence from multiple document types
- Performs reasoning across the retrieved evidence
- Generates a grounded response with source citations
- Flags uncertainty whenever sufficient evidence is unavailable

This implementation intentionally focuses on a **small synthetic dataset (17 document chunks across 3 document types)** instead of the complete enterprise-scale platform described in the challenge.

---

# Why I Chose This Approach

I intentionally built this project using technologies I already had practical experience with instead of introducing unfamiliar frameworks under a strict deadline.

Key reasons behind the design:

- Reused the **Flask + IBM Granite** integration pattern from my previous **Startup Blueprint Generator** project.
- The assignment explicitly allows a **single tool-using agent** operating over **10–30 documents**, making an in-memory retrieval pipeline appropriate.
- Focused on building a reliable retrieval → reasoning → citation workflow instead of spending time configuring external vector databases or orchestration frameworks.
- Used technologies I could confidently explain and justify during evaluation.

---

# System Architecture

```text
User Question (UI / API)
        │
        ▼
Flask API (/query)
Bearer Token Authentication
        │
        ▼
Sentence Embedding
(sentence-transformers)
        │
        ▼
Cosine Similarity Search
(NumPy In-Memory)
        │
        ▼
Top Relevant Chunks
Orders • Refunds • Support Tickets
        │
        ▼
Python Orchestrator
(Multi-source Evidence Retrieval)
        │
        ▼
IBM Granite (watsonx.ai)
Grounded Prompt
        │
        ▼
Answer + Citations + Confidence Flag
        │
        ▼
Browser UI / JSON API Response
```

### Retrieval Layer

- Documents are loaded during startup.
- Split into semantic chunks.
- Embedded once using Sentence Transformers.
- Stored in-memory as NumPy vectors.
- User queries are embedded and matched using cosine similarity.

### Reasoning Layer

A Python orchestrator retrieves relevant evidence from:

- Orders
- Refunds
- Support Tickets

before making **one grounded LLM call**, ensuring the model reasons across multiple sources rather than answering from a single document.

### Evidence Layer

The prompt instructs the model to:

- Cite document types and record IDs
- Avoid unsupported assumptions
- Explicitly mention missing information
- Flag low-confidence responses

---

# Tech Stack

| Component | Technology |
|-----------|------------|
| API Framework | Flask |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector Search | NumPy Cosine Similarity (In-Memory) |
| LLM | IBM Granite (`granite-4-h-small`) via watsonx.ai |
| Alternate LLM | Groq (`llama-3.3-70b-versatile`) |
| Data Processing | pandas |
| Frontend | HTML + Vanilla JavaScript |
| Deployment | Docker (CPU-only PyTorch) |

---

# Project Structure

```text
novacart-insight-assistant/
│
├── app/
│   ├── __init__.py
│   ├── ingest.py              # Loads and chunks documents
│   ├── retrieve.py            # Embeddings + similarity search
│   ├── orchestrator.py        # Multi-document reasoning
│   ├── main.py                # Flask API + routes
│   │
│   └── static/
│       └── index.html         # Browser UI
│
├── data/
│   ├── orders.csv
│   ├── refunds.csv
│   └── support_tickets.txt
│
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# Setup Instructions

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd novacart-insight-assistant
```

---

## 2. Configure Environment Variables

Copy `.env.example` to `.env`

```env
GRANITE_API_KEY=your_ibm_cloud_api_key

WATSONX_PROJECT_ID=your_project_id

WATSONX_URL=https://us-south.ml.cloud.ibm.com

API_AUTH_TOKEN=choose_any_secret_token
```

Optional (Groq)

```env
GROQ_API_KEY=your_groq_api_key
```

---

## 3. Run Locally

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python -m app.main
```

Open:

```
http://localhost:5000
```

---

## 4. Run with Docker

Build

```bash
docker build -t novacart-insight .
```

Run

```bash
docker run -p 5000:5000 --env-file .env novacart-insight
```

Open:

```
http://localhost:5000
```

---

# API Usage

## Health Endpoint

```http
GET /health
```

Example

```bash
curl http://localhost:5000/health
```

Response

```json
{
  "status": "ok"
}
```

---

## Query Endpoint

```http
POST /query
```

Requires:

- Bearer Authentication
- Token must match `API_AUTH_TOKEN`

Example

```bash
curl -X POST http://localhost:5000/query \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <API_AUTH_TOKEN>" \
-d '{
      "question":"Why was the mechanical keyboard order refunded twice?"
}'
```

Example Response

```json
{
  "question": "Why was the mechanical keyboard order refunded twice?",
  "answer": "The mechanical keyboard order (orders/ORD1005) was refunded twice because the initial refund was issued for a defective unit, and a second refund was processed after the replacement also failed.",
  "sources": [
    {
      "doc_type": "orders",
      "record_id": "ORD1005"
    },
    {
      "doc_type": "refunds",
      "record_id": "REF2002"
    },
    {
      "doc_type": "support_tickets",
      "record_id": "TCK3004"
    }
  ]
}
```

---

# Dataset

The project uses a **synthetic business dataset** consisting of **17 document chunks** across **3 document types**.

| Document | Description |
|-----------|-------------|
| `orders.csv` | 7 order records (including one intentional duplicate) |
| `refunds.csv` | 5 refund records linked through `order_id` |
| `support_tickets.txt` | 4 support tickets plus one outdated policy note |

The dataset is intentionally cross-linked through shared **order_id** values to enable **multi-hop reasoning**.

### Example Reasoning Chain

```
ORD1005
      │
      ▼
Support Ticket #1
      │
      ▼
Refund #1
      │
      ▼
Replacement Order
      │
      ▼
Support Ticket #2
      │
      ▼
Refund #2
```

This allows the assistant to correctly answer questions such as:

> **"Why was the mechanical keyboard order refunded twice?"**

---

# Previous Work Reused

### Startup Blueprint Generator

Reused:

- Flask application structure
- IBM Granite integration
- Grounded prompting approach

Modified for:

- Document retrieval
- Evidence-backed reasoning
- Multi-source citation

---

### MedAce

Reused:

- Multi-format document ingestion pipeline

Simplified by removing:

- Chat history
- Conversational memory

---

### SQL & Data Analytics Projects

Applied prior experience with structured business datasets while designing the synthetic NovaCart data.

---

# Current Limitations

- Aggregation/counting queries are less reliable because retrieval only searches the top-k semantic matches rather than the complete dataset.
- Citation misattribution may occasionally occur for closely related records.
- In-memory retrieval is suitable only for small datasets and does not scale to large document collections.
- No reranking stage after retrieval.
- No conversational memory between requests.
- Authentication uses a simple API token intended only for demonstration.
- No automated evaluation benchmark for retrieval quality.

---

# Future Improvements

- Replace in-memory search with **pgvector** or **Qdrant**.
- Add a reranking model after retrieval.
- Route aggregation queries directly to SQL/pandas instead of semantic retrieval.
- Add citation verification before returning responses.
- Introduce conversational memory.
- Implement production-grade authentication and authorization.
- Build an automated evaluation framework with expected evidence sources and retrieval metrics.
