from src.pdf_loader import extract_text_from_pdf
from src.chunker import create_chunks
from src.embeddings import create_embeddings
from src.faiss_index import create_faiss_index
from src.agent import run_agent

from pathlib import Path
import pickle
import faiss


INDEX_FILE = Path("data/faiss.index")
CHUNKS_FILE = Path("data/chunks.pkl")


def build_rag():

    # Check whether a saved RAG index already exists
    if INDEX_FILE.exists() and CHUNKS_FILE.exists():

        print("Loading saved RAG index...")

        index = faiss.read_index(str(INDEX_FILE))

        with open(CHUNKS_FILE, "rb") as f:
            all_chunks = pickle.load(f)

        documents = [
            chunk["text"]
            for chunk in all_chunks
        ]

        print("Saved RAG index loaded.")

        return index, documents, all_chunks


    print("Building RAG index for the first time...")

    pdf_folder = Path("data/papers")

    pdf_files = list(pdf_folder.glob("*.pdf"))

    print("Total PDFs:", len(pdf_files))

    all_chunks = [] 

    for pdf_path in pdf_files:

        print(f"\nProcessing: {pdf_path.name}")

        pages = extract_text_from_pdf(str(pdf_path))

        print("Total pages:", len(pages))

        chunks = create_chunks(
            pages,
            pdf_path.name
        )

        print("Total chunks:", len(chunks))

        all_chunks.extend(chunks)


    documents = [
        chunk["text"]
        for chunk in all_chunks
    ]


    chunk_embeddings = create_embeddings(
        documents
    )

    print("Embeddings created")


    index = create_faiss_index(
        chunk_embeddings
    )

    print("FAISS index created")


    # Save FAISS index
    faiss.write_index(
        index,
        str(INDEX_FILE)
    )


    # Save chunks
    with open(CHUNKS_FILE, "wb") as f:

        pickle.dump(
            all_chunks,
            f
        )


    print("RAG index saved.")

    return index, documents, all_chunks


if __name__ == "__main__":

    index, documents, all_chunks = build_rag()

    query = input("\nAsk your question: ")

    result = run_agent(
        query,
        index,
        documents,
        all_chunks
    )

    print("\nFinal answer:")
    print(result)