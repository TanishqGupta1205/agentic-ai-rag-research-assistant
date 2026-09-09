# 🤖 Agentic AI RAG Research Assistant

An **Agentic RAG-based research assistant** that allows users to upload research papers and ask questions about them.

The system retrieves relevant information from uploaded papers, evaluates whether the retrieved context is sufficient, and can refine the search query when the initial retrieval is not sufficient before generating a grounded answer with source and page references.

The application uses a **React frontend** with a **FastAPI backend** and a FAISS-based retrieval pipeline.

---

## 🚀 Features

- 📄 Upload one or multiple research papers in PDF format
- ✂️ Split extracted paper text into smaller chunks
- 🧠 Generate semantic embeddings using Sentence Transformers
- 🔎 Perform similarity search using FAISS
- 🤖 Agent-based context evaluation
- 🔄 Iterative query refinement when retrieved context is insufficient
- 📚 Retrieve information from multiple uploaded research papers
- 📝 Generate answers using a Groq-hosted LLM
- 📌 Display source paper and page references
- 💬 Maintain chat history for multiple questions
- 🧠 Display the Agent Process used to generate the answer
- 📊 Evaluate responses using Context Relevance, Answer Relevance, and Faithfulness
- 🗑️ Clear uploaded documents and chat history
- ⚡ Cache processed documents and embeddings for faster startup
- 🌐 React frontend with FastAPI backend

---

## 🧠 How It Works

The application follows an agentic retrieval workflow:

```text
                  User Question
                       ↓
                 Query Embedding
                       ↓
                  FAISS Search
                       ↓
                 Relevant Chunks
                       ↓
            Context Relevance Evaluation
                       ↓
                  Agent Decision
                  ┌─────┴─────┐
                 NO           YES
                 ↓              ↓
           Refine Query    Generate Answer
                 ↓              ↓
            Search Again   Answer Relevance
                 │              ↓
                 │         Faithfulness
                 │              ↓
                 │       Source + Page Info
                 │
                 └── Repeat (max 3 attempts)
                           ↓
                  If still insufficient
                           ↓
             Return "Not enough information found"
🛠️ Tech Stack
Frontend
React.js
Vite
React Markdown
CSS
Backend
Python
FastAPI
Uvicorn
AI / RAG
FAISS — Vector similarity search
Sentence Transformers — Text embeddings
Groq — LLM inference
PyPDF2 — PDF text extraction
NumPy
python-dotenv
📁 Project Structure
research_agent/
│
├── data/
│   ├── faiss.index
│   ├── chunks.pkl
│   └── papers/
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
├── backend/
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── main.py
├── requirements.txt
└── README.md
⚙️ Backend Setup
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd research_agent
2. Create a virtual environment
python -m venv venv

Activate it on Windows:

venv\Scripts\activate
3. Install Python dependencies
pip install -r requirements.txt
4. Configure the Groq API key

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key_here

Make sure .env is included in .gitignore.

🎨 Frontend Setup

Open another terminal:

cd frontend

Install the frontend dependencies:

npm install

Start the React development server:

npm run dev

The frontend will run at:

http://localhost:5173
▶️ Run the Application
Start the FastAPI backend

From the project root:

uvicorn backend.main:app --reload

The backend will run at:

http://localhost:8000
Start the React frontend

From the frontend directory:

npm run dev

The frontend will run at:

http://localhost:5173

Open the frontend URL in your browser.

📄 Using the Application
1. Upload Research Papers

Select a PDF using the Upload PDF option.

The backend:

PDF
 ↓
Text Extraction
 ↓
Chunking
 ↓
Embedding Generation
 ↓
FAISS Index

The uploaded document is then added to the active knowledge base.

2. Ask Questions

Enter a question about the uploaded research papers.

The system retrieves relevant chunks and evaluates the retrieved context.

3. Agentic Retrieval

If the first retrieval attempt does not provide sufficient context, the agent refines the search query and performs another retrieval attempt.

Example:

Search attempt 1
        ↓
Context insufficient
        ↓
Query refinement
        ↓
Search attempt 2
        ↓
Context sufficient
        ↓
Answer generation

The interface displays this process in the Agent Process section.

4. View Evaluation

Each answer is evaluated using:

Context Relevance
Answer Relevance
Faithfulness
5. View Sources

The system displays the source document and page number associated with retrieved information.

Example:

paper5.pdf — Page 4
paper5.pdf — Page 7
paper5.pdf — Page 3
6. Chat History

Multiple questions can be asked within the same session.

Each question keeps its:

Answer
Agent Process
Evaluation scores
Sources
7. Clear Documents

The Clear Documents option removes the active document collection and clears the chat history.

💡 Example Questions

You can ask questions such as:

What is the paper about?

What problems does the paper address?

What challenges are discussed?

What methods are proposed?

What are the limitations mentioned in the paper?

How does the proposed method work?

What are the key findings?

What applications are discussed?
🤖 Agentic Behavior

Unlike a basic RAG chatbot that retrieves information once and immediately generates an answer, this project includes an agentic decision step.

The agent:

Receives the user's question.
Retrieves relevant document chunks.
Evaluates whether the retrieved context is sufficient.
If the context is insufficient, generates a refined search query.
Performs another retrieval attempt.
Repeats the process for a limited number of attempts.
Generates the final answer when sufficient information is found.
Evaluates the generated answer using Context Relevance, Answer Relevance, and Faithfulness.
Returns the answer along with source and page references.

The React interface displays the Agent Process so users can understand how the system reached the final answer.

📌 Source Attribution

Retrieved chunks contain metadata for:

Source PDF
Page number

The final response uses this metadata to display where the retrieved information came from.

Example:

paper5.pdf — Page 4
paper5.pdf — Page 7
paper5.pdf — Page 3
🔐 Environment Variables

The project uses a .env file for the Groq API key.

Example:

GROQ_API_KEY=your_groq_api_key_here

Make sure .env is included in .gitignore.

Recommended .gitignore entries:

.env
venv/
__pycache__/
*.pyc
node_modules/
dist/
📊 RAG Evaluation

The system evaluates generated responses using three metrics:

Context Relevance

Measures whether the retrieved information is relevant to the user's question.

Answer Relevance

Measures whether the generated answer directly addresses the user's question.

Faithfulness

Measures whether the claims in the generated answer are supported by the retrieved context.

Example:

Context Relevance: 1.0
Answer Relevance: 1.0
Faithfulness: 1.0
⚡ Document and Embedding Caching

The application saves the processed FAISS index and document chunks to reduce startup time.

The saved files include:

data/faiss.index
data/chunks.pkl

When a new PDF is uploaded, embeddings are generated for the newly added chunks and added to the existing FAISS index.

🔮 Future Improvements

Planned improvements include:

Live Agent Process streaming
Improved citation-aware answer generation
Better retrieval and reranking
Persistent vector database for larger document collections
User authentication and document isolation
More advanced agent orchestration
Larger research-paper test dataset
Cloud deployment and production monitoring
🎯 Project Goal

The goal of this project is to build a research assistant that can work with a user's own collection of research papers and provide:

Document-grounded answers
Source and page attribution
Agentic retrieval and query refinement
Response quality evaluation

The system is designed to reduce unsupported answers by grounding responses in retrieved research-paper content.

🏗️ Application Architecture
                    React Frontend
                         │
                         │ HTTP
                         ↓
                    FastAPI Backend
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
          Upload       Ask       Clear
             │           │
             ↓           ↓
        PDF Processing  Agent
             │           │
             ↓           ↓
        Chunk + Embed   Retrieval
             │           ↓
             ↓      Context Evaluation
         FAISS ←───────┤
             │         ↓
             │     Query Refinement
             │         ↓
             │     Answer Generation
             │         ↓
             │       Evaluation
             │         ↓
             └──→ Sources + Answer

Built with React, FastAPI, Python, FAISS, Sentence Transformers, Groq, and PyPDF2.