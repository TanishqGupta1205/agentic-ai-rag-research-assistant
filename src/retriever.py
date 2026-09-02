def retrieve_documents(query, embeddings_model, index, documents, all_chunks, top_k=3):
    query_embedding = embeddings_model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    retrieved_docs = [all_chunks[i] for i in indices[0]]
    return retrieved_docs