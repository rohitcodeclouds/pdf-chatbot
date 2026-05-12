# 📄 PDF Chatbot using LangChain & Groq

An AI-powered PDF Chatbot built with Python, Streamlit, LangChain, FAISS, HuggingFace Embeddings, and Groq LLM.

Upload any PDF document and ask questions in natural language to get accurate, context-aware answers directly from the document using Retrieval-Augmented Generation (RAG).

---

# 🚀 Features

- 📂 Upload PDF documents
- 🔍 Semantic search using vector embeddings
- 🤖 AI-powered question answering
- ⚡ Fast retrieval using FAISS vector database
- 🧠 Context-aware responses with RAG pipeline
- 💬 Interactive Streamlit UI
- 📑 Intelligent text chunking
- 🔐 Session state management for optimized performance

---

# 🛠️ Tech Stack

- Python
- Streamlit
- LangChain
- FAISS
- HuggingFace Embeddings
- OPENAI API
- Groq API
- pdfplumber

---

# 📂 Project Structure

```bash
pdf-chatbot/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── uploads/
└── README.md
```

---

# ⚙️ Installation

## 1️⃣ Clone the Repository

```bash
[git clone https://github.com/rohitcodeclouds/pdf-chatbot.git]
```

---

## 2️⃣ Navigate to Project Folder

```bash
cd pdf-chatbot
```

---

## 3️⃣ Create Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate environment:

```bash
.venv\Scripts\activate
```

---

### Mac/Linux

```bash
python3 -m venv .venv
```

Activate environment:

```bash
source .venv/bin/activate
```

---

## 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the root directory.

Add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key
```

Get API Key from:

https://console.groq.com/keys

---

# ▶️ Run the Application

```bash
streamlit run app.py
```

---

# 💡 How It Works

1. Upload a PDF document
2. Extract text using pdfplumber
3. Split text into chunks
4. Generate embeddings using HuggingFace
5. Store embeddings in FAISS vector database
6. Retrieve relevant context
7. Generate AI-powered answers using Groq LLM

---

# 📸 Preview

The application allows users to:

- Upload PDFs
- Ask questions about uploaded documents
- Receive context-aware answers instantly

---

# 🔮 Future Improvements

- Multiple PDF uploads
- Chat history support
- OCR support for scanned PDFs
- Source citations with page numbers
- Conversation memory
- PDF summarization
- Download chat history

---

# 🧠 AI Concepts Used

- Retrieval-Augmented Generation (RAG)
- Vector Embeddings
- Semantic Search
- Similarity Search
- Large Language Models (LLMs)

---

# 👨‍💻 Author

Developed by Sweety ✨

---

# 📜 License

This project is licensed under the MIT License.
