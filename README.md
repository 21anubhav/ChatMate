# ChatMate

# ChatMate – AI-Powered Document-Aware Chatbot

ChatMate is an **AI-powered chatbot** that allows users to upload documents, store them in a **vector database**, and have **real-time, context-aware conversations** based on the uploaded content.  
It integrates **LangChain** for text processing, **Pinecone** for vector storage, and **MySQL** for user authentication and metadata management.

---

## 🚀 Features

- **User Authentication** – Secure login & signup system using MySQL.
- **Document Upload & Storage** – Upload PDFs or text files for knowledge base creation.
- **Vector Database Integration** – Store document embeddings in Pinecone for fast retrieval.
- **LangChain-Powered Text Processing** – Chunk and preprocess documents with `RecursiveCharacterTextSplitter`.
- **Context-Aware Responses** – Retrieve relevant chunks for improved chatbot answers.
- **Scalable Backend** – Built with FastAPI and SQLAlchemy for efficient performance.
- **Virtual Environment Support** – Isolated Python environment for dependency management.

---

## 🛠 Technologies Used

- **Python 3.11**
- **FastAPI** – Backend API framework
- **SQLAlchemy** – ORM for MySQL
- **MySQL** – Relational database for user data & document metadata
- **LangChain** – Text chunking & retrieval-augmented generation
- **Pinecone** – Vector database for storing document embeddings
- **MySQL Connector/Python** – Database connectivity
- **Uvicorn** – ASGI server

---

## 📂 Project Structure

