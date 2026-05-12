import os.path

import pdfplumber
import streamlit as st
from dotenv import load_dotenv
import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from streamlit.runtime import uploaded_file_manager
from tiktoken import model

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.markdown("""
    <style>
        /* Target sidebar header */
        [data-testid="stSidebarHeader"]::before {
            content: "Codeclouds Chatbot";
            display: block;
            text-align: center;
            font-size: 18px;
            font-weight: 600;
            margin-top: 10px;
            color: white;
        }
        section.stMain{
             position: fixed;
            top: 50%;
            left: 60%;
            transform: translate(-50%, -50%);
            width: 100%;
            display: flex;
            justify-content: center;
        }
        label[data-testid="stWidgetLabel"] {
            display: block;
            text-align: center;
        }
        
        /* Make sidebar container full height */
        [data-testid="stSidebar"] > div:first-child {
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* Push user content to bottom */
        [data-testid="stSidebarUserContent"] {
            margin-top: auto;
            padding-bottom: 1rem;
        }
        
        .stTextInput [data-testid="stMarkdownContainer"] p{
                font-size: 30px;
                padding-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)
# st.header("Codeclouds Chatbot")
def UploadDoc():
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    st.title("Upload File")
    file = st.file_uploader("Upload a PDF file and start asking QA", type="PDF")
    if file is not None:
        file_path = os.path.join(UPLOAD_DIR, file.name)

        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        st.success(f"Saved: {file_path}")
    return file

# Upload the file using Streamlit library
with st.sidebar:
   file = UploadDoc()

#Get user question
question = st.text_input("What’s on your mind today?", placeholder="Type your question…")

#Extract contents from the uploaded file and Chunk it
if question:
    if file is not None:
        #extract text from it
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        #st.write(text)

        #Split extracted code into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', "\n", ". ", " ", ""],
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = text_splitter.split_text(text)
        #st.write(chunks)

        #Generating embeddings after chunking in text
        embeddings = OpenAIEmbeddings(
            model='text-embedding-3-small',
            openai_api_key = OPENAI_API_KEY,
        )

        #Store embeddings into vector_db
        #Here we are using FAISS vector db which is from META
        vector_store = FAISS.from_texts(chunks, embeddings)

        #generate answer
        #questions -> embeddings -> similarity_search -> results to LLM -> response/answer

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # Here similiary_search is happening for both
        # pdf & question embedding is getting compared
        retriever = vector_store.as_retriever(
            search_type = 'mmr', # mmr is a search technique
            search_kwargs = {"k":4}, #It's return the 4 closet match
        )

        # Define LLM
        llm = ChatOpenAI(
            model = "gpt-4o-mini",
            tempurature = "0.3",
            has_tokens = 1000,
            openai_api_type = OPENAI_API_KEY,
        )


        # provide the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("script",
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

        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()} |
            prompt |
            llm |
            StrOutputParser()
        )

        response = chain.invoke(question)
        st.write(response)
    else :
        st.write ("No document found.\n\n"
            "👉 Please upload a PDF first, then ask your question."
        )