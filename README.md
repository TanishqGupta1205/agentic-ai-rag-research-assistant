## 🤖 Agentic AI RAG Research Assistant

An **Agentic RAG-based research assistant** that allows users to upload research papers and ask questions about them.

The system retrieves relevant information from uploaded papers, evaluates whether the retrieved context is sufficient, and can refine the search query when the initial retrieval is not sufficient before generating a grounded answer with source and page references.

## 🚀 Features

- 📄 Upload one or multiple research papers in PDF format
- ✂️ Split extracted paper text into smaller chunks
- 🧠 Generate semantic embeddings using Sentence Transformers
- 🔎 Perform similarity search using FAISS
- 🤖 Agent-based context evaluation
- 🔄 Iterative query refinement when retrieved context is insufficient
- 📚 Retrieve information from multiple research papers
- 📝 Generate answers using a Groq-hosted LLM
- 📌 Display source paper and page references
- 💬 Streamlit chat interface
- 🗑️ Clear chat history
- ⚡ Cache processed documents and embeddings for faster interaction

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
        ┌───┴───┐
       NO      YES
       ↓         ↓
 Refine Query   Generate Answer
       ↓             ↓
  Search Again   Answer Relevance
       │             ↓
       │        Faithfulness
       │             ↓
       │      Source + Page Info
       │
       └─── Repeat (max 3 attempts)
                  ↓
        If still insufficient
                  ↓
          Return "Not enough
           information found"

## 🛠️ Tech Stack

- **Python**
- **Streamlit** — Web interface
- **FAISS** — Vector similarity search
- **Sentence Transformers** — Text embeddings
- **Groq** — LLM inference
- **PyPDF2** — PDF text extraction
- **NumPy**
- **python-dotenv**

## 📁 Project Structure

```text
research_agent/
│
├── data/
│   └── papers/
│       ├── paper1.pdf
│       ├── paper2.pdf
│       └── ...
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
├── app.py
├── main.py
├── requirements.txt
└── README.md

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd research_agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser.

Upload one or more research papers and start asking questions.

## 💡 Example Questions

You can ask questions such as:

```text
What is image processing according to the paper?
What are the weaknesses of region-based segmentation?
What problems are discussed in the paper?
How does image segmentation affect object detection performance?
What challenges does computer vision face according to the paper?
```

## 🤖 Agentic Behavior

Unlike a basic RAG chatbot that retrieves information once and immediately generates an answer, this project includes an agentic decision step.

The agent:

1. Receives the user's question.
2. Retrieves relevant document chunks.
3. Evaluates whether the retrieved context is sufficient.
4. If the context is insufficient, generates a refined search query.
5. Performs another retrieval attempt.
6. Repeats the process for a limited number of attempts.
7. Generates the final answer when sufficient information is found.
8. Evaluates the generated answer using Context Relevance, Answer Relevance, and Faithfulness.
9. Returns the answer along with source and page references.

The Streamlit interface also provides a **View Agent Process** section so users can see the retrieval, evaluation, query refinement, and answer-generation workflow.

## 📌 Source Attribution

Retrieved chunks contain metadata for:

- Source PDF
- Page number

The final response uses this metadata to display where the retrieved information came from.

## 🔐 Environment Variables

The project uses a `.env` file for the Groq API key.

Example:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Make sure `.env` is included in `.gitignore`.

Recommended `.gitignore` entries:

```text
.env
venv/
__pycache__/
*.pyc
```
## 📊 RAG Evaluation

The system evaluates generated responses using three metrics:

- **Context Relevance** — measures whether retrieved information is relevant to the user's question.
- **Answer Relevance** — measures whether the generated answer directly addresses the question.
- **Faithfulness** — measures whether the claims in the generated answer are supported by the retrieved context.

## 🔮 Future Improvements

Planned improvements include:

- Better retrieval and query refinement
- Improved citation-aware answer generation
- FastAPI backend
- React frontend
- Persistent vector database for larger document collections
- More advanced agent orchestration
- Larger research-paper test dataset

## 🎯 Project Goal

The goal of this project is to build a research assistant that can work with a user's own collection of research papers and provide **document-grounded answers with an agentic retrieval workflow**.

---

Built with Python, FAISS, Sentence Transformers, Groq, and Streamlit.
