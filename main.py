from src.pdf_loader import extract_text_from_pdf
from src.chunker import create_chunks
from src.embeddings import create_embeddings
from src.faiss_index import create_faiss_index
from src.agent import run_agent
from pathlib import Path

pdf_folder = Path("data/papers")
pdf_files=list(pdf_folder.glob("*.pdf"))
print("Total PDFs:", len(pdf_files))


all_chunks=[]
for pdf_path in pdf_files:
    print(f"\nProcessing:{pdf_path.name}")
    pages=extract_text_from_pdf(str(pdf_path))
    print("Total pages:",len(pages))
    chunks=create_chunks(pages,pdf_path.name)
    print("Total chunks:",len(chunks))
    all_chunks.extend(chunks)

# 3. Get text from chunks
documents = [chunk["text"] for chunk in all_chunks]
# 4. Create embeddings
chunk_embeddings = create_embeddings(documents)

print("Embeddings created")


# 5. Create FAISS index
index = create_faiss_index(chunk_embeddings)

print("FAISS index created")
query=input("\nAsk your question:")
answer=run_agent(
    query,
    index,
    documents,
    all_chunks
)
print("\n Final answer:")
print(answer)