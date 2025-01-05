import streamlit as st
import pandas as pd
import pdfplumber

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# # Jupyter-specific imports
# from IPython.display import display, Markdown

# Set environment variable for protobuf
import os
import glob
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

#####AIK#####
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

#Streamlit page configuration
st.set_page_config(
    page_title="Resume Chat Pro",
    layout="wide",
)

#AI model
selected_model = "llama3.2"

def create_vector_db():
    job_roles = [
            "",  # Blank option
            "Software Development", "Data Science", "Product Management", "Design", 
            "Marketing", "Sales", "Human Resources", "Customer Support", 
            "Finance", "Project Management", "Content Creation", "UI/UX Design", 
            "Business Analysis", "Engineering", "Cybersecurity", "Operations", 
            "Production", "Other"
        ]

    job_role = st.selectbox("Please select job role from dropdown", job_roles, key="job_role")
    with st.spinner(":green[Loading...]"):
        folder_path = os.path.join("uploaded_resumes", job_role)
        pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

        data = []
        total_chunks = []
        if pdf_files:

            # Load PDF files
            for pdf_file in pdf_files:
                loader = UnstructuredPDFLoader(file_path=pdf_file)
                pdf_data = loader.load()
                data.append(pdf_data)
                relative_path = os.path.relpath(pdf_file, start="uploaded_resumes")
                st.markdown(f"PDF loaded successfully: {relative_path}")

            # Split text into chunks
            for pdf_data in data:
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                chunks = text_splitter.split_documents(pdf_data)
                total_chunks.append(chunks)
                # st.text(f"Text split into {len(chunks)} chunks")
                # st.text(chunks)

            # Flatten the list of chunks
            all_chunks = [chunk for sublist in total_chunks for chunk in sublist]
            
            # Create vector database using all chunks
            vector_db = Chroma.from_documents(
                documents=all_chunks,
                embedding=OllamaEmbeddings(model="nomic-embed-text"),
                collection_name="local-rag"
            )
            st.markdown("Vector database created successfully, let's chat!")
            return vector_db

        elif job_role == "":
            st.markdown("")
        else:
            st.markdown("There is no resume uploaded in the selected job role.")

def process_question(question, vector_db):
    
    # Initialize LLM
    llm = ChatOllama(model=selected_model)
    
    # Query prompt template
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate 2 
        different versions of the given user query aimed at retrieving relevant candidate 
        resume data from a vector database. By crafting multiple perspectives on the query, 
        your goal is to ensure comprehensive and relevant matches for analyzing candidate 
        qualifications, skills, and experiences, while addressing potential limitations of 
        distance-based similarity searches. Provide these alternative queries separated by newlines.
        Original question: {question}""",
    )

    # Set up retriever
    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(), 
        llm,
        prompt=QUERY_PROMPT
    )

    # RAG prompt template
    template = """Answer the question based ONLY on the following context:
    {context}
    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    # Create chain
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    response = chain.invoke(question)
    return response

@st.cache_data
def extract_all_pages_as_images(pdf_file):
    pdf_pages = []
    with pdfplumber.open(pdf_file) as pdf:
        pdf_pages = [page.to_image().original for page in pdf.pages]
    return pdf_pages

# Main function
def main():
    # Create layout
    st.markdown("## 🤖 **Resume Chat Pro - Local AI Companion on your workspace**")
    st.markdown("""
                Welcome to **Resume Chat Pro**—your AI-powered assistant for analyzing resumes 
                and exploring candidate qualifications, skills, and experiences. Choose a job role 
                and start uncovering insights instantly!
    """)

    # Ensure session state is initialized
    if "vector_db" not in st.session_state:
        st.session_state["vector_db"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Clear vector DB if switching between job roles
    if st.session_state["vector_db"] is not None:
        st.session_state["vector_db"].delete_collection()
        st.session_state["vector_db"] = None

    # Create vector DB
    st.session_state["vector_db"] = create_vector_db()

    #chat interface
    message_container = st.container()
    for i, message in enumerate(st.session_state["messages"]):
        avatar = "🤖" if message["role"] == "assistant" else "😎"
        with message_container.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Display chat history
    # for i, message in enumerate(st.session_state["messages"]):
    #     avatar = "🤖" if message["role"] == "assistant" else "😎"
    #     with message_container.chat_message(message["role"], avatar=avatar):
    #         st.markdown(message["content"])

    # Chat input and processing
    if prompt := st.chat_input("Enter a prompt here...", key="chat_input"):
        try:
            # Add user message to chat
            st.session_state["messages"].append({"role": "user", "content": prompt})
            with message_container.chat_message("user", avatar="😎"):
                st.markdown(prompt)

            # Process and display assistant response
            with message_container.chat_message("assistant", avatar="🤖"):
                with st.spinner(":green[processing...]"):
                    if st.session_state["vector_db"] is not None:
                        response = process_question(
                            prompt, st.session_state["vector_db"]
                        )
                        st.markdown(response)
                    else:
                        st.warning("Please select job role with resume to begin chat...")

            # Add assistant response to chat history
            if st.session_state["vector_db"] is not None:
                st.session_state["messages"].append(
                    {"role": "assistant", "content": response}
                )

        except Exception as e:
            st.error(e, icon="⛔️")
    else:
        if st.session_state["vector_db"] is None:
            st.warning("Select job role with resume to begin chat...")


if __name__ == "__main__":
    main()