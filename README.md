# Complaint Categorization and RAG System

An AI-powered complaint management platform that automatically processes consumer complaints, assigns product and sub-product categories using LLM-based classification, and leverages a Retrieval-Augmented Generation (RAG) pipeline to surface similar historical complaints. The system transforms unstructured complaint data into actionable insights, enabling faster resolution times and pattern detection across large volumes of consumer feedback. Built with a focus on scalability and production-readiness, it demonstrates how vector similarity search can enhance complaint handling workflows in financial services and beyond.

![Submit Complaint](Screenshot%202026-02-05%20230951.jpg)

The core workflow begins when a complaint is submitted through the frontend interface. The text is immediately processed through our embedding service, which generates a dense vector representation using the `all-MiniLM-L6-v2` sentence-transformer model running locally. This embedding is stored alongside the complaint metadata in PostgreSQL using the pgvector extension, which enables native vector operations without requiring a separate vector database. Simultaneously, the complaint text is sent to the Mistral API for categorization, where the LLM analyzes the content and returns structured JSON containing product categories, sub-products, and issue classifications. The system then performs a cosine similarity search against the existing complaint corpus, retrieving the top-k most similar complaints based on semantic similarity rather than keyword matching.

![Dashboard](Screenshot%202026-02-05%20231049.jpg)

The RAG pipeline injects these retrieved complaints as contextual evidence into the LLM prompt, allowing the model to make more informed categorization decisions by comparing against real historical data. This approach significantly improves accuracy, especially for edge cases or ambiguous complaints that might be misclassified in isolation. Once categorized, the system generates concise summaries using the same LLM, extracting key details like the core issue, affected parties, and resolution status. All of this happens asynchronously through FastAPI's background task system, ensuring the API remains responsive even during heavy processing loads. The frontend provides real-time feedback and displays similar complaints alongside the submitted one, giving users immediate visibility into related issues.

![Browse Complaints](Screenshot%202026-02-05%20231201.jpg)

From an architectural standpoint, the backend is built on FastAPI with SQLAlchemy ORM handling database interactions. PostgreSQL serves as both the relational store and vector database through pgvector, eliminating the need for external vector services like Pinecone or Qdrant. This unified approach reduces operational complexity and latency, as vector searches happen in the same transaction context as metadata queries. The embedding service uses sentence-transformers for local inference, keeping costs down while maintaining reasonable performance for batch operations. On the frontend, React with TypeScript provides a clean, responsive interface that communicates with the REST API, displaying categorized complaints, analytics dashboards with Recharts visualizations, and filtering capabilities for browsing the complaint database.

![Complaint Details](Screenshot%202026-02-05%20231222.jpg)

The system delivers tangible value by automating what would otherwise be manual categorization work, reducing processing time from hours to seconds per complaint. Financial institutions can quickly identify systemic issues across product lines, detect fraud patterns, and ensure compliance with regulatory reporting requirements. The similarity search functionality enables customer service teams to reference how similar complaints were resolved historically, improving consistency and reducing training overhead. Analytics dashboards surface trends in complaint volume, product-specific issues, and geographic distributions, enabling data-driven decision-making at the executive level.

For production deployment, the plan is to migrate to AWS services, leveraging RDS PostgreSQL with pgvector for managed database hosting, SageMaker for embedding model inference at scale, and Bedrock for LLM interactions to reduce API costs. The roadmap includes integrating additional modules: a ticketing system for complaint lifecycle management, call support integration to capture voice complaints and convert them to text, and a voice agent powered by Amazon Connect and Lex for automated complaint intake. The goal is to build a fully integrated complaint management ecosystem where complaints can enter through multiple channels—web forms, phone calls, emails, or API submissions—and flow through a unified processing pipeline with consistent categorization, routing, and tracking capabilities.

## Quick Start

See [setup.md](setup.md) for detailed installation and setup instructions.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL + pgvector
- **AI/ML**: sentence-transformers (all-MiniLM-L6-v2), Mistral API
- **Frontend**: React, TypeScript, Vite, Recharts
- **Infrastructure**: Docker, Docker Compose
