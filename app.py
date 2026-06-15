import streamlit as st

from graphs.analytics_graph import build_graph
from services.upload_service import UploadService
from services.rebuild_service import RebuildService


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
    "Upload CSV files and ask questions about your data."
)


# ==========================================
# Upload CSVs
# ==========================================

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

    try:

        with st.spinner(
            "Preparing datasets..."
        ):

            rebuild_service = (
                RebuildService()
            )

            rebuild_service.rebuild()

            # Refresh LangGraph cache
            get_graph.clear()

        st.success(
            "Contexts and embeddings rebuilt!"
        )

    except Exception as error:

        st.error(
            f"Rebuild failed:\n{error}"
        )


# ==========================================
# Session State
# ==========================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ==========================================
# Display Chat History
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ==========================================
# Chat Input
# ==========================================

question = st.chat_input(
    "Ask a question..."
)


# ==========================================
# Process Question
# ==========================================

if question:

    # --------------------------------------
    # Display User Message
    # --------------------------------------

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

            "final_response": None,

            "generated_code": None,

            "execution_result": None
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

        response = {

            "type": "error",

            "data": str(error)
        }

    # --------------------------------------
    # Display Assistant Response
    # --------------------------------------

    with st.chat_message("assistant"):

        if isinstance(response, dict):

            response_type = response.get(
                "type"
            )

            # ------------------------------
            # DataFrame
            # ------------------------------

            if response_type == "dataframe":

                st.dataframe(
                    response["data"]
                )

                chat_content = (
                    response["data"]
                    .to_string()
                )

            # ------------------------------
            # Series
            # ------------------------------

            elif response_type == "series":

                st.dataframe(
                    response["data"]
                )

                chat_content = str(
                    response["data"]
                )

            # ------------------------------
            # Text
            # ------------------------------

            elif response_type == "text":

                st.markdown(
                    response["data"]
                )

                chat_content = response[
                    "data"
                ]

            # ------------------------------
            # Error
            # ------------------------------

            elif response_type == "error":

                st.error(
                    response["data"]
                )

                chat_content = (
                    "Error: "
                    + response["data"]
                )

            # ------------------------------
            # Unknown Dict
            # ------------------------------

            else:

                st.markdown(
                    str(response)
                )

                chat_content = str(
                    response
                )

        else:

            st.markdown(response)

            chat_content = response

    # --------------------------------------
    # Save Assistant Message
    # --------------------------------------

    st.session_state.messages.append({

        "role": "assistant",

        "content": chat_content
    })