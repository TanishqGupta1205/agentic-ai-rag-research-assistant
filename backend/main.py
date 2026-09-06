from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from main import build_rag
from src.agent import run_agent
from src.pdf_loader import extract_text_from_pdf
from src.chunker import create_chunks
from src.embeddings import create_embeddings
from src.faiss_index import create_faiss_index
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
index, documents, all_chunks = build_rag()

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def home():
    return {
        "message": "FastAPI is working"
    }

@app.post("/ask")
def ask_question(request:QuestionRequest):
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

    new_chunks = []
    uploaded_files = []

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

        finally:

            os.remove(temp_path)

    if not new_chunks:
        raise HTTPException(
            status_code=400,
            detail="No readable content found in the uploaded PDFs"
        )

    all_chunks.extend(new_chunks)

    documents = [
        chunk["text"]
        for chunk in all_chunks
    ]

    chunk_embeddings = create_embeddings(
        documents
    )

    index = create_faiss_index(
        chunk_embeddings
    )

    return {
        "message": "PDFs uploaded successfully",
        "files": uploaded_files,
        "chunks_added": len(new_chunks),
        "total_chunks": len(all_chunks)
    }
@app.delete("/clear")
def clear_documents():
    global index,documents,all_chunks
    all_chunks=[]
    documents=[]
    index=None
    return{
        "message":"All uploaded documents cleared"
    }