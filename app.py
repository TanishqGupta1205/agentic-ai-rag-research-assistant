import streamlit as st
import tempfile
import os

from src.pdf_loader import extract_text_from_pdf
from src.chunker import create_chunks
from src.embeddings import create_embeddings
from src.faiss_index import create_faiss_index
from src.agent import run_agent


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="📚",
    layout="centered"
)


# --------------------------------------------------
# Custom UI Styling
# --------------------------------------------------

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background: linear-gradient(
            135deg,
            #f5f7ff 0%,
            #eef2ff 50%,
            #f8fafc 100%
        );
    }

    /* Main title */
    h1 {
        color: #312e81;
        font-weight: 700;
    }

    /* Normal text */
    p {
        color: #334155;
    }

    /* Success message */
    .stAlert {
        border-radius: 12px;
    }

    /* Uploaded papers box */
    div[data-testid="stExpander"] {
        border-radius: 12px;
        border: 1px solid #c7d2fe;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        border: 1px solid #6366f1;
        color: #4338ca;
        background-color: white;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #eef2ff;
        border-color: #4338ca;
    }

    /* Chat input */
    div[data-testid="stChatInput"] {
        border-radius: 12px;
    }

    /* Agent process box */
    .agent-box {
        background: #eef2ff;
        border-left: 5px solid #6366f1;
        padding: 15px;
        border-radius: 10px;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .agent-title {
        font-weight: 700;
        color: #312e81;
        margin-bottom: 8px;
    }

    .agent-step {
        color: #475569;
        margin: 5px 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Build FAISS index from uploaded PDFs
# --------------------------------------------------

@st.cache_resource
def build_index(file_data):

    all_chunks = []

    for file_name, file_bytes in file_data:

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        temp_file.write(file_bytes)
        temp_file.close()

        pages = extract_text_from_pdf(
            temp_file.name
        )

        chunks = create_chunks(
            pages,
            file_name
        )

        all_chunks.extend(chunks)

        os.remove(temp_file.name)

    documents = [
        chunk["text"]
        for chunk in all_chunks
    ]

    chunk_embeddings = create_embeddings(
        documents
    )

    index = create_faiss_index(
        chunk_embeddings
    )

    return index, documents, all_chunks


# --------------------------------------------------
# UI
# --------------------------------------------------

st.title("📚 AI Research Assistant")

st.write(
    "Upload research papers and ask questions about them."
)


# --------------------------------------------------
# PDF Upload
# --------------------------------------------------

uploaded_files = st.file_uploader(
    "Upload Research Papers",
    type=["pdf"],
    accept_multiple_files=True
)


# --------------------------------------------------
# Main application
# --------------------------------------------------

if uploaded_files:

    file_data = tuple(
        (file.name, file.getvalue())
        for file in uploaded_files
    )

    with st.spinner(
        "Processing research papers..."
    ):

        index, documents, all_chunks = build_index(
            file_data
        )

    st.success(
        f"{len(uploaded_files)} research paper(s) processed successfully!"
    )


    # --------------------------------------------------
    # Uploaded Papers
    # --------------------------------------------------

    with st.expander("📄 Uploaded Papers"):

        for file in uploaded_files:

            st.write(
                f"• {file.name}"
            )


    # --------------------------------------------------
    # Chat history
    # --------------------------------------------------

    if "messages" not in st.session_state:

        st.session_state.messages = []


    # --------------------------------------------------
    # Clear Chat
    # --------------------------------------------------

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()


    # --------------------------------------------------
    # Display previous messages
    # --------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )

            # Show agent process for previous answers
            if (
                message["role"] == "assistant"
                and "agent_steps" in message
            ):

                with st.expander("🤖 View Agent Process"):

                    for step in message["agent_steps"]:

                        st.write(step)


    # --------------------------------------------------
    # Question input
    # --------------------------------------------------

    query = st.chat_input(
        "Ask a question about your research papers..."
    )


    # --------------------------------------------------
    # Generate answer
    # --------------------------------------------------

    if query:

        # Display user question
        with st.chat_message("user"):

            st.write(query)


        # Save user question
        st.session_state.messages.append(
            {
                "role": "user",
                "content": query
            }
        )


        # Store agent steps
        agent_steps = []


        def progress_callback(message):

            agent_steps.append(message)


        # Generate AI answer
        with st.chat_message("assistant"):

            with st.spinner(
                "Research agent is working..."
            ):

                answer = run_agent(
                    query,
                    index,
                    documents,
                    all_chunks,
                    progress_callback
                )


            # --------------------------------------------------
            # Agent Process
            # --------------------------------------------------

            with st.expander(
                "🤖 View Agent Process",
                expanded=False
            ):

                for step in agent_steps:

                    st.write(step)


            # --------------------------------------------------
            # Final Answer
            # --------------------------------------------------

            st.write(answer)


        # Save AI answer + agent process
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "agent_steps": agent_steps
            }
        )


else:

    st.info(
        "👆 Upload one or more research papers to get started."
    )