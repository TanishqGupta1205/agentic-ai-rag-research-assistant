from sentence_transformers import SentenceTransformer
embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(documents):

    return embeddings_model.encode(documents)