from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from src.agent import run_agent
from src.pdf_loader import extract_text_from_pdf
from src.chunker import create_chunks
from src.embeddings import create_embeddings

import os
import tempfile
import pickle
import faiss
import asyncio
import json
import queue


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Make sure data folder exists
os.makedirs("data", exist_ok=True)


# Start with an empty knowledge base.
# PDFs are added only through /upload.
index = None
documents = []
all_chunks = []


class QuestionRequest(BaseModel):
    question: str


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "FastAPI is working"
    }


# --------------------------------------------------
# Normal Ask endpoint
# --------------------------------------------------

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


# --------------------------------------------------
# Live Agent Process endpoint
# --------------------------------------------------

@app.post("/ask-stream")
async def ask_question_stream(request: QuestionRequest):

    if index is None or not all_chunks:

        async def error_stream():

            yield (
                "event: error\n"
                f"data: {json.dumps('No documents are currently loaded.')}\n\n"
            )

        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream"
        )

    progress_queue = queue.Queue()

    def progress_callback(message):
        progress_queue.put(message)

    # Run the synchronous agent in a background thread
    agent_task = asyncio.create_task(
        asyncio.to_thread(
            run_agent,
            request.question,
            index,
            documents,
            all_chunks,
            progress_callback
        )
    )

    async def generate():

        # Send live agent steps
        while True:

            while True:

                try:

                    message = progress_queue.get_nowait()

                    yield (
                        "event: step\n"
                        f"data: {json.dumps(message)}\n\n"
                    )

                    # Give the client time to receive/render the step
                    await asyncio.sleep(0.05)

                except queue.Empty:
                    break

            if agent_task.done():
                break

            await asyncio.sleep(0.05)

        # Send any remaining steps
        while True:

            try:

                message = progress_queue.get_nowait()

                yield (
                    "event: step\n"
                    f"data: {json.dumps(message)}\n\n"
                )

                await asyncio.sleep(0.05)

            except queue.Empty:
                break

        # Send final result
        try:

            result = await agent_task

            yield (
                "event: result\n"
                f"data: {json.dumps(result)}\n\n"
            )

        except Exception as error:

            yield (
                "event: error\n"
                f"data: {json.dumps(str(error))}\n\n"
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# --------------------------------------------------
# Upload PDF
# --------------------------------------------------

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

    # Create FAISS index if it does not exist
    if index is None:

        index = faiss.IndexFlatL2(
            new_embeddings.shape[1]
        )

    # Add embeddings to FAISS
    index.add(new_embeddings)

    print("New embeddings added to FAISS index")

    # Save updated FAISS index
    faiss.write_index(
        index,
        "data/faiss.index"
    )

    # Save updated chunks
    with open("data/chunks.pkl", "wb") as f:

        pickle.dump(
            all_chunks,
            f
        )

    print("Updated RAG index saved")

    return {
        "message": "PDFs uploaded successfully",
        "files": uploaded_files,
        "chunks_added": total_chunks_added,
        "total_chunks": len(all_chunks)
    }


# --------------------------------------------------
# Clear documents
# --------------------------------------------------

@app.delete("/clear")
def clear_documents():

    global index, documents, all_chunks

    all_chunks = []
    documents = []
    index = None

    # Delete saved FAISS index
    if os.path.exists("data/faiss.index"):

        os.remove(
            "data/faiss.index"
        )

    # Delete saved chunks
    if os.path.exists("data/chunks.pkl"):

        os.remove(
            "data/chunks.pkl"
        )

    return {
        "message": "All uploaded documents cleared"
    }