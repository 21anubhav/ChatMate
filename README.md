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
chatmate/
│── backend/
│ ├── main.py # FastAPI entry point
│ ├── database.py # MySQL connection setup
│ ├── models.py # SQLAlchemy models
│ ├── init_db.py # Database initialization
│ ├── pinecone_utils.py # Pinecone integration functions
│ └── auth.py # User authentication logic
│── venv/ # Virtual environment
│── requirements.txt # Dependencies
│── README.md # Project documentation




---
📌 Usage

Sign up / Log in to your account

Upload a document (PDF or TXT)

Ask questions – ChatMate will respond based on your document’s content

---

🎯 Key Highlights

Retrieval-Augmented Generation (RAG) for intelligent Q&A

Document-aware conversations

Efficient text chunking using LangChain

Real-time vector search with Pinecone

---
Anubhav Singh Pathania

GitHub: https://github.com/21anubhav

LinkedIn: https://linkedin.com/in/anubhavsinghpathania

---
## ⚙️ Installation

1️⃣ **Clone the repository**  
```bash
git clone https://github.com/your-username/chatmate.git
cd chatmate

2️⃣ python -m venv venv
source venv/bin/activate   # For Mac/Linux
venv\Scripts\activate      # For Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Set up MySQL Database
CREATE DATABASE chatbot;
CREATE USER 'chatbot_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON chatbot.* TO 'chatbot_user'@'localhost';
FLUSH PRIVILEGES;

5️⃣ Configure Environment Variables
Create a .env file in the root directory:
DATABASE_URL=mysql+mysqlconnector://chatbot_user:your_password@localhost/chatbot
PINECONE_API_KEY=your_pinecone_api_key

6️⃣ Initialize Database
python backend/init_db.py

7️⃣ Run the Backend
uvicorn backend.main:app --reload



