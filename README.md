# NovaCart Insight Assistant — Design & Implementation Document

### Horrazon AI — Round II Engineering Challenge


# 1. Problem Statement

NovaCart Global's business data is spread across multiple systems such as orders, refunds, support tickets, warehouse logs, and supplier reports. Since these systems are disconnected, answering a business question like *"Why did refunds increase last month?"* requires manually checking different documents and combining information from multiple teams. This process is slow and difficult to verify.

The objective of this prototype is to build a Retrieval-Augmented Generation (RAG) system that accepts natural language queries, retrieves relevant information from different document types, reasons across the retrieved evidence, and generates a final answer with source citations while indicating uncertainty whenever sufficient evidence is unavailable.

---

# 2. Abstract

For this challenge, I built a lightweight RAG prototype with a simple multi-step reasoning workflow over a synthetic dataset containing orders, refunds, and support ticket records.

Instead of using a vector database or a complex agent framework, I chose an in-memory embedding index using NumPy cosine similarity because it is lightweight, reliable, and sufficient for the given dataset size. A single orchestrator function retrieves relevant information from multiple document types before sending all collected evidence to IBM Granite (via watsonx.ai) to generate the final response.

The application is exposed through a Flask REST API (`/query` and `/health`) and containerized using Docker. My focus was on building a system that is easy to understand, explain, and extend rather than introducing unnecessary infrastructure.

---

# 3. Why I Chose This Approach

I selected this approach mainly because it builds on technologies I have already worked with.

* I reused the Flask and IBM Granite integration from my Startup Blueprint Generator project, where prompt grounding and structured responses helped reduce hallucinations.
* The challenge itself mentions that a single tool-using agent and a small document collection are sufficient, so using an in-memory retrieval mechanism fits the requirements without adding unnecessary complexity.
* Rather than spending time configuring external databases or orchestration frameworks, I focused on implementing reliable retrieval, reasoning, and evidence citation.
* Since I am already familiar with Flask, NumPy, and watsonx.ai, I can confidently explain every design decision made in this implementation.

---

# 4. System Architecture

```
User Question
      │
      ▼
Flask API (/query)
      │
      ▼
Query Embedding
      │
      ▼
Cosine Similarity Search (NumPy)
      │
      ▼
Top Relevant Chunks
(Orders, Refunds, Support Tickets)
      │
      ▼
Orchestrator Function
      │
      ▼
IBM Granite (Grounded Prompt)
      │
      ▼
Final Answer
+ Source Citations
+ Confidence / Uncertainty
      │
      ▼
JSON Response
```

### Retrieval Layer

All documents are loaded during startup, divided into chunks, embedded once, and stored in memory. When a user submits a query, cosine similarity is used to retrieve the most relevant chunks from each document category.

### Reasoning Layer

A single Python orchestrator retrieves evidence from multiple document types before making one LLM call. This allows the model to combine information from different sources instead of answering from a single document.

### Evidence Layer

The prompt instructs the model to:

* cite the documents and record IDs used,
* avoid unsupported assumptions,
* clearly mention when information is incomplete,
* provide an uncertainty flag if confidence is low.

---

# 5. Previous Work Used

### Startup Blueprint Generator Agent
- **Reused:** Flask API structure, IBM Granite integration, grounded prompting.
- **Modified:** Replaced the startup knowledge base with NovaCart business documents and redesigned prompts for evidence-based reasoning.

### MedAce
- **Reused:** Multi-format document ingestion pipeline.
- **Modified:** Simplified the ingestion pipeline by removing chat history and retaining only document processing.

### SQL & Data Analytics Projects
- **Reused:** Understanding of structured business data.
- **Applied:** Used this experience while designing the synthetic NovaCart dataset.
---

# 6. Advantages of My Approach

* Uses technologies I already have experience with, making the implementation reliable.
* No external vector database is required, reducing setup complexity.
* Meets all the core requirements of the assignment, including retrieval, reasoning, citations, and REST APIs.
* The retrieval module is independent, making it easy to replace the NumPy index with pgvector, Chroma, or Qdrant in the future.

---

# 7. Implementation Plan

 Tasks.....                                                           |
 
 Create project structure (`data`, `app`, `Dockerfile`, `README`)     |
 
 Generate synthetic datasets for orders, refunds, and support tickets |
 
 Build document ingestion and chunking pipeline                       |
 
 Generate embeddings and store them in a NumPy array                  |
 
 Implement cosine similarity retrieval                                |
 
 Build the orchestrator to collect evidence across document types     |
 
 Integrate IBM Granite through watsonx.ai                             |
 
 Develop Flask `/query` and `/health` endpoints                       |
 
 Containerize the application using Docker                            |
 
 Prepare README and architecture documentation                        |
 
 Record demo video and push final code to GitHub                      |

---

# 8. Current Limitations and Future Improvements

* The in-memory retrieval approach is suitable only for small datasets. For larger collections, I would use pgvector or Qdrant.
* There is no reranking stage, which could improve retrieval accuracy for complex queries.
* The system is stateless and does not support multi-turn conversations.
* Authentication currently uses a simple API key and can be replaced with proper user authentication in a production environment.
* A dedicated evaluation framework with predefined test queries and expected evidence would help measure retrieval quality more objectively.

