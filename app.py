import streamlit as st
from graphs.analytics_graph import build_graph
from services.upload_service import UploadService
from services.rebuild_service import (
    RebuildService
)


# ==========================================
# Cache Graph
# ==========================================

@st.cache_resource
def get_graph():

    return build_graph()


# ==========================================
# Streamlit Config
# ==========================================

st.set_page_config(
    page_title="CSV Analytics Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CSV Analytics Agent")

st.write(
    "Ask questions about your datasets."
)
uploaded_files = st.file_uploader(
    "Upload CSV files",
    type=["csv"],
    accept_multiple_files=True
)
if uploaded_files:

    upload_service = UploadService()

    saved_paths = upload_service.save_files(
        uploaded_files
    )

    st.success(
        f"{len(saved_paths)} file(s) uploaded."
    )

    st.write(saved_paths)

    with st.spinner(
        "Preparing datasets..."
    ):

        rebuild_service = (
            RebuildService()
        )

        rebuild_service.rebuild()
        get_graph.clear()

    st.success(
        "Contexts and embeddings rebuilt!"
    )

    upload_service = UploadService()

    saved_paths = upload_service.save_files(
        uploaded_files
    )

    st.success(
        f"{len(saved_paths)} file(s) uploaded."
    )

    st.write(saved_paths)


# ==========================================
# Session State
# ==========================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ==========================================
# Display History
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ==========================================
# User Input
# ==========================================

question = st.chat_input(
    "Ask a question..."
)


# ==========================================
# Process Query
# ==========================================

if question:

    st.session_state.messages.append({

        "role": "user",

        "content": question
    })

    with st.chat_message("user"):

        st.markdown(question)

    try:

        graph = get_graph()

        initial_state = {

            "question": question,

            "parsed_query": None,

            "retrieval_result": None,

            "analysis_result": None,

            "final_response": None
        }

        with st.spinner(
            "Analyzing..."
        ):

            result = graph.invoke(
                initial_state
            )

        response = result[
            "final_response"
        ]

    except Exception as error:

        response = (
            f"Backend Error:\n{error}"
        )

    with st.chat_message(
        "assistant"
    ):

        st.markdown(response)

    st.session_state.messages.append({

        "role": "assistant",

        "content": response
    })