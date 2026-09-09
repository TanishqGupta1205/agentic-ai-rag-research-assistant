from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from src.agent import run_agent
from src.pdf_loader import extract_text_from_pdf
from src.chunker import create_chunks
from src.embeddings import create_embeddings
from fastapi.middleware.cors import CORSMiddleware

import os
import tempfile
import pickle
import faiss


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Start with an empty knowledge base.
# PDFs are added only through /upload.
index = None
documents = []
all_chunks = []
class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "FastAPI is working"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):

    if index is None or not all_chunks:
        raise HTTPException(
            status_code=400,
            detail="No documents are currently loaded."
        )

    result = run_agent(
        request.question,
        index,
        documents,
        all_chunks
    )

    return {
        "question": request.question,
        **result
    }


@app.post("/upload")
async def upload_pdfs(files: list[UploadFile] = File(...)):

    global index, documents, all_chunks

    print("UPLOAD STARTED")

    new_chunks = []
    uploaded_files = []
    total_chunks_added = 0

    for file in files:

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} is not a PDF"
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(await file.read())
            temp_path = temp_file.name

        try:

            pages = extract_text_from_pdf(temp_path)

            chunks = create_chunks(
                pages,
                file.filename
            )

            new_chunks.extend(chunks)
            uploaded_files.append(file.filename)

            total_chunks_added += len(chunks)

        finally:

            os.remove(temp_path)

    if not new_chunks:
        raise HTTPException(
            status_code=400,
            detail="No readable content found in the uploaded PDFs"
        )

    print("New PDF chunks:", len(new_chunks))

    # Create embeddings only for newly uploaded chunks
    new_documents = [
        chunk["text"]
        for chunk in new_chunks
    ]

    print("Creating embeddings for new chunks...")

    new_embeddings = create_embeddings(
        new_documents
    )

    print("New embeddings created")

    # Add new chunks to existing data
    all_chunks.extend(new_chunks)

    documents = [
        chunk["text"]
        for chunk in all_chunks
    ]

    # Add new embeddings to existing FAISS index
    if index is None:
        index = faiss.IndexFlatL2(
            new_embeddings.shape[1]
        )

    index.add(new_embeddings)

    print("New embeddings added to FAISS index")

    # Save updated index
    faiss.write_index(
        index,
        "data/faiss.index"
    )

    # Save updated chunks
    with open("data/chunks.pkl", "wb") as f:
        pickle.dump(all_chunks, f)

    print("Updated RAG index saved")

    return {
        "message": "PDFs uploaded successfully",
        "files": uploaded_files,
        "chunks_added": total_chunks_added,
        "total_chunks": len(all_chunks)
    }

@app.delete("/clear")
def clear_documents():

    global index, documents, all_chunks

    all_chunks = []
    documents = []
    index = None

    # Delete saved RAG index
    if os.path.exists("data/faiss.index"):
        os.remove("data/faiss.index")

    # Delete saved chunks
    if os.path.exists("data/chunks.pkl"):
        os.remove("data/chunks.pkl")

    return {
        "message": "All uploaded documents cleared"
    }