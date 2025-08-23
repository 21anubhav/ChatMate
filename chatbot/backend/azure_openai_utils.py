import os
import re
from typing import Optional, AsyncGenerator, List
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
from backend.pinecone_utils import index

load_dotenv()

# Initialize Azure OpenAI client
client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-05-01-preview",
)

embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
chat_model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")


# 🔹 Generate embeddings for list of text chunks
async def embed_text(chunks: List[str]) -> List[List[float]]:
    response = await client.embeddings.create(input=chunks, model=embedding_model)
    return [item.embedding for item in response.data]


# 🔹 Format markdown-like output to HTML
def format_markdown_to_html(text: str) -> str:
    # Clean up malformed newlines or repeated segments
    text = re.sub(r"(To turn on.*?)\1+", r"\1", text, flags=re.IGNORECASE)

    # Replace bullets
    text = re.sub(r"^\s*[-•]\s+", "- ", text, flags=re.MULTILINE)

    # Bold: **text**
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)

    # Italic: *text*
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)

    # Remove markdown headings (e.g., ##, ###)
    text = re.sub(r"#+\s*", "", text)

    # Convert numbered lists like "1. Item"
    text = re.sub(r"^(\d+)\.\s+", r"\1. ", text, flags=re.MULTILINE)

    # Replace line breaks with <br>
    text = text.replace("\n", "<br>")

    return text.strip()


# 🔹 Non-streaming chat (used in /guest-chat)
async def chat_with_documents(
    query: str, namespace: str, selected_file: Optional[str] = None
) -> str:
    if not query or not query.strip():
        return "Please enter a valid question."

    try:
        embedded_query = await embed_text([query])
        query_vector = embedded_query[0]

        search_result = index.query(
            vector=query_vector, top_k=5, include_metadata=True, namespace=namespace
        )

        matches = search_result.get("matches", [])
        if selected_file:
            matches = [m for m in matches if m["metadata"].get("file") == selected_file]

        context = "\n".join(
            m["metadata"].get("text", "") for m in matches if "text" in m["metadata"]
        )

        if not context.strip():
            return "I couldn’t find relevant information in your documents."

        system_prompt = (
            "You are an intelligent assistant. Use the context below to answer questions:\n\n"
            f"{context}\n\n"
            "If the answer is not in the context, reply: 'I don’t know based on the document.'"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        response = await client.chat.completions.create(
            model=chat_model, messages=messages, temperature=0.2, max_tokens=800
        )

        raw_output = response.choices[0].message.content
        return format_markdown_to_html(raw_output)

    except Exception as e:
        print(f"[Chat Error] {e}")
        return "An error occurred while generating the answer. Please try again."


# 🔹 Streaming chat response (used in /guest-chat/stream)
async def stream_chat_with_documents(
    query: str, namespace: str, selected_file: Optional[str] = None
) -> AsyncGenerator[str, None]:
    if not query.strip():
        yield "Please enter a valid question."
        return

    try:
        embedded_query = await embed_text([query])
        query_vector = embedded_query[0]

        search_result = index.query(
            vector=query_vector, top_k=5, include_metadata=True, namespace=namespace
        )

        matches = search_result.get("matches", [])
        if selected_file:
            matches = [m for m in matches if m["metadata"].get("file") == selected_file]

        context = "\n".join(
            m["metadata"].get("text", "") for m in matches if "text" in m["metadata"]
        )

        if not context.strip():
            yield "I couldn’t find relevant information in your documents."
            return

        system_prompt = (
            "You are an intelligent assistant. Use the context below to answer questions:\n\n"
            f"{context}\n\n"
            "If the answer is not in the context, reply: 'I don’t know based on the document.'"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        response = await client.chat.completions.create(
            model=chat_model,
            messages=messages,
            temperature=0.2,
            max_tokens=800,
            stream=True,
        )

        buffer = ""

        async for chunk in response:
            delta = chunk.choices[0].delta.content if chunk.choices else ""
            if delta:
                buffer += delta
                if " " in buffer or "\n" in buffer:
                    parts = re.split(r"(\s+)", buffer)
                    completed = "".join(parts[:-1])
                    buffer = parts[-1]
                    yield completed

        if buffer.strip():
            yield buffer

    except Exception as e:
        print(f"[Streaming Chat Error] {e}")
        yield "An error occurred while generating the answer. Please try again."
