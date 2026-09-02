import faiss


def create_faiss_index(chunk_embeddings):

    dimension = chunk_embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(chunk_embeddings)

    return index