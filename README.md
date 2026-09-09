# 🤖 Agentic AI RAG Research Assistant

An **Agentic RAG-based research assistant** that allows users to upload research papers and ask questions about them.

The system retrieves relevant information from uploaded PDFs, evaluates the retrieved context, refines the search query when needed, and generates grounded answers with source and page references.

## 🚀 Features

- 📄 Upload research papers in PDF format
- ✂️ Extract and chunk PDF text
- 🧠 Generate embeddings using Sentence Transformers
- 🔎 Semantic search using FAISS
- 🤖 Context relevance evaluation
- 🔄 Automatic query refinement when context is insufficient
- 📝 Generate answers using Groq LLM
- 📌 Source and page references
- 💬 Chat history for multiple questions
- 📊 Answer evaluation using Context Relevance, Answer Relevance, and Faithfulness
- 🗑️ Clear documents and chat history
- 🌐 React frontend with FastAPI backend

## 🧠 How It Works

```text
User Question
      ↓
Query Embedding
      ↓
FAISS Search
      ↓
Relevant Chunks
      ↓
Context Evaluation
      ↓
Is Context Sufficient?
    ↙       ↘
  No         Yes
  ↓           ↓
Refine      Generate
Query       Answer
  ↓           ↓
Search      Evaluate
Again       Answer
              ↓
        Sources + Answer
```

## 🛠️ Tech Stack

### Frontend
- React.js
- Vite
- React Markdown
- CSS

### Backend
- Python
- FastAPI
- Uvicorn

### AI / RAG
- FAISS
- Sentence Transformers
- Groq
- PyPDF2
- NumPy
- python-dotenv

## 📁 Project Structure

```text
research_agent/
│
├── backend/
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   └── package.json
│
├── src/
│   ├── pdf_loader.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── faiss_index.py
│   ├── retriever.py
│   ├── llm.py
│   ├── agent.py
│   └── evaluator.py
│
├── main.py
├── requirements.txt
└── README.md
```

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/TanishqGupta1205/agentic-ai-rag-research-assistant.git
cd agentic-ai-rag-research-assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Do not upload `.env` to GitHub.

## ▶️ Run the Application

### Start FastAPI

From the project root:

```bash
uvicorn backend.main:app --reload
```

Backend:

```text
http://localhost:8000
```

### Start React

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## 💡 Example Questions

```text
What is the paper about?

What problems does the paper address?

What challenges are discussed?

What methods are proposed?

What are the limitations of the paper?

What are the key findings?
```

## 🤖 Agentic Behavior

Unlike a basic RAG system that retrieves documents once, this project evaluates the retrieved context before generating an answer.

The agent can:

1. Retrieve relevant chunks.
2. Evaluate context relevance.
3. Refine the query if the context is insufficient.
4. Search again.
5. Generate a grounded answer.
6. Evaluate the generated answer.
7. Provide source and page references.

## 📊 Evaluation

The system evaluates responses using:

- **Context Relevance** — relevance of retrieved information.
- **Answer Relevance** — how well the answer addresses the question.
- **Faithfulness** — whether the answer is supported by the retrieved context.

## 🔮 Future Improvements

- Live Agent Process streaming
- Better retrieval and reranking
- Persistent vector database
- User authentication
- Cloud deployment
- Improved citation handling

## 🎯 Project Goal

The goal is to build a research assistant that can work with a user's own research papers and provide **grounded, source-backed answers** using an **agentic retrieval workflow**.

---

Built with **React, FastAPI, Python, FAISS, Sentence Transformers, Groq, and PyPDF2**.