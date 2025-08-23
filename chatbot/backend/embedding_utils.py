# backend/embedding_utils.py
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-05-01-preview"
)

embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

# Get embeddings from Azure OpenAI
async def embed_text(chunks: list[str]) -> list[list[float]]:
    result = client.embeddings.create(
        input=chunks,
        model=embedding_model
    )
    return [r.embedding for r in result.data]
