import os
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from backend.embedding_utils import embed_text

# Setup Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))


# Split text into chunks
def read_and_split_text(file_path, chunk_size=1000, chunk_overlap=100):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)


# Store embeddings in Pinecone
async def embed_and_store(file_path: str, namespace: str):
    chunks = read_and_split_text(file_path)
    embeddings = await embed_text(chunks)

    pinecone_vectors = [
        {"id": str(uuid.uuid4()), "values": emb, "metadata": {"text": chunk}}
        for chunk, emb in zip(chunks, embeddings)
    ]
    index.upsert(vectors=pinecone_vectors, namespace=namespace)


# Delete vectors from a specific file within a namespace
def delete_namespace_file(file_path: str, namespace: str):
    chunks = read_and_split_text(file_path)

    # Query top_k with dummy vector to retrieve potential matches
    dummy_vector = [0.0] * 1536  # Ensure this matches your embedding dimension
    response = index.query(
        namespace=namespace, top_k=100, include_metadata=True, vector=dummy_vector
    )

    ids_to_delete = []
    for match in response.get("matches", []):
        if match["metadata"].get("text") in chunks:
            ids_to_delete.append(match["id"])

    if ids_to_delete:
        index.delete(ids=ids_to_delete, namespace=namespace)


def delete_namespace(namespace: str):
    """
    Delete all vectors in a namespace (e.g. for guest session or full user reset).
    """
    index.delete(delete_all=True, namespace=namespace)
