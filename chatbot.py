import pdfplumber
import os
import os.path
import streamlit as st
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_groq import ChatGroq

load_dotenv()

# =========================
# Session State
# =========================
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None



# =========================
# Functions
# =========================
def upload_file(uploaded_file):
    upload_folder  = './uploads'
    if not os.path.exists(upload_folder) :
        os.makedirs(upload_folder, exist_ok=True)

    if uploaded_file is not None:
        file_path = os.path.join(
            upload_folder,
            uploaded_file.name
        )
        with open(file_path, "wb") as f:
            file_buffer = uploaded_file.getbuffer()
            f.write(file_buffer)
        st.success(f"Uploaded file: {uploaded_file.name}")
        return file_path
    return None


def chunk_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " ", ""],
            chunk_size=1000,
            chunk_overlap=200
        )

        textchunks = text_splitter.split_text(text)

        st.write(textchunks)

        return textchunks


def embedding_text():
    # Embeddings the file
    # embedding = HuggingFaceEmbeddings(
    #     model_name='intfloat/e5-base-v2'
    # )
    embedding = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2'
    )
    # st.write("Embedding created successfully")
    # st.write(embeddings)
    return embedding

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def retriever_data():
    data = st.session_state.vector_store.as_retriever(
        search_type = 'mmr', #mmr is search technique
        search_kwargs = {"k":4}
    )
    return data


def initialize_grok_llm() :
    model = ChatGroq(
        model = "llama-3.1-8b-instant",
        temperature = 0.3,
        max_tokens=1000,
    )
    return model

def prompt_guide() :
    prompt = ChatPromptTemplate.from_messages([
        ("system",
        "You are helpful assistant answering questions about a pdf documnetation.\n\n"
        "Guidelines: \n"
        "Core Rules:\n"
        "1. Use ONLY the provided context. Do NOT use outside knowledge.\n"
        "2. Do NOT assume, infer, or guess beyond what is explicitly written.\n"
        "3. If the answer is missing or unclear, respond with:\n"
        "   'The information is not available in the provided context.'\n\n"

        "Answering Guidelines:\n"
        "4. Provide clear, complete, and well-structured answers:\n"
        "   - Use bullet points for lists or steps.\n"
        "   - Use tables for comparisons or structured data.\n"
        "   - Use short paragraphs for explanations.\n"
        "   - Highlight important terms or numbers where relevant.\n"
        "   - Do not overuse tables if simple text is sufficient.\n"
        "5. Include relevant details such as numbers, definitions, and explanations.\n"
        "6. Summarize long information concisely without losing key meaning.\n"
        "7. Do NOT copy large chunks of the context—paraphrase intelligently.\n\n"

        "Citations:\n"
        "8. Wherever possible, support your answer with short references or quotes from the context.\n\n"

        "Handling Complex Queries:\n"
        "9. Break down multi-part or complex questions into smaller parts before answering.\n"
        "10. If the question is ambiguous, ask a clarification question instead of guessing.\n\n"

        "Output Format (STRICT):\n"
        "Return your response in the following structure:\n\n"
        "Answer:\n"
        "<your main answer>\n\n"
        "Key Points:\n"
        "- point 1\n"
        "- point 2\n\n"
        "Context Reference:\n"
        "<relevant excerpt or summary from context>\n\n"
        "Context :\n {context}"
    ),
    ("human", "{question}")
    ])

    return prompt


# =========================
# Sidebar
# =========================

with st.sidebar:
    st.title("📄 PDF Chatbot")
    st.subheader('Recent Uploads', divider=True)

    uploaded_file = st.file_uploader("Choose a file", type="PDF")
    file = None

    if uploaded_file is not None:
        # Process only new file
        if(st.session_state.uploaded_filename != uploaded_file.name):
            st.session_state.file_processed = False
            st.session_state.vector_store = None
            st.session_state.uploaded_filename = uploaded_file.name

            file = upload_file(uploaded_file)
        else:
            file = os.path.join(
                "./uploads",
                uploaded_file.name
            )

    # =========================
    # Process PDF
    # =========================
    # Chunking Uploaded file
    if file and not st.session_state.file_processed:
        with st.spinner("Processing PDF..."):
            chunks = chunk_text(file)
            embeddings = embedding_text()
            # Store embeddings into vector_db
            # Here we are using FAISS vector db which is from META
            vector_store = FAISS.from_texts(chunks, embeddings)
            st.session_state.vector_store = vector_store
            st.session_state.file_processed = True
            st.write("PDF processed successfully ✅")
            # st.write(vector_store)



# =========================
# Main Panel
# =========================
#Text Input created
user_question = st.text_input(
    "Ask a question...",
    placeholder="Enter your question..."
)


if user_question:
    if st.session_state.vector_store is not None:
            #Process to Generated Answer
            #questions -> embeddings -> similarity search -> result to LLM -> response/answer
            with st.spinner("Searching similarities..."):
                retriever = retriever_data()
                llm = initialize_grok_llm()
                prompt = prompt_guide()

                chain = (
                    {
                        "context": retriever | RunnableLambda(format_docs),
                        "question": RunnablePassthrough()
                    }
                    | prompt
                    | llm
                    | StrOutputParser()

                )

                response = chain.invoke(user_question)
                st.write(response)
    else :
        st.write("No document found.\n\n"
                 "👉 Please upload a PDF first, then ask your question."
                 )
