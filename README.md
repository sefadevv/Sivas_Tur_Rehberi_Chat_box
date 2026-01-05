# 🏛️ Sivas City Guide AI (Sivas Şehir Rehberi)

This project is an advanced AI-powered assistant designed to guide users through the city of Sivas. Built with a modern tech stack, it leverages **Retrieval-Augmented Generation (RAG)** to answer questions based on uploaded PDF documents and integrates real-time **Google Search** for up-to-date information.

## 🌟 Key Features

* **Hybrid Intelligence:** Combines the power of **Ollama (Gemma Model)** with real-time web search results via SerpAPI.
* **RAG Architecture:** Allows users to upload PDF documents (e.g., historical texts, travel guides), which are processed using **FAISS** vector store and **HuggingFace Embeddings** for context-aware answers.
* **Modern Architecture:** Decoupled backend (**FastAPI**) and frontend (**Streamlit**) for scalability and clean code structure.
* **Interactive UI:** A user-friendly chat interface that supports streaming responses and session management.

## 🛠️ Tech Stack

* **Backend:** FastAPI, Uvicorn
* **Frontend:** Streamlit
* **LLM Orchestration:** LangChain, Ollama
* **Vector Store:** FAISS
* **Search Engine:** SerpAPI (Google Search)
