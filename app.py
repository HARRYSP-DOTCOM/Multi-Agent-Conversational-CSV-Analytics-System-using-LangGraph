import streamlit as st
import pandas as pd

from graphs.analytics_graph import build_graph
from services.upload_service import UploadService
from services.rebuild_service import RebuildService
from agents.analysis_agent import clear_dataset_cache


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

            rebuild_service = RebuildService()

            rebuild_service.rebuild()

            # Clear cached graph
            get_graph.clear()

            # Clear cached datasets
            clear_dataset_cache()

            # Reset chat history
            st.session_state.messages = []

        st.success(
            "Contexts and embeddings rebuilt successfully!"
        )

        st.info(
            "New datasets are now active."
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

        content = message["content"]

        if isinstance(content, pd.DataFrame):

            st.dataframe(
                content,
                use_container_width=True
            )

        elif isinstance(content, pd.Series):

            st.dataframe(
                content.to_frame(),
                use_container_width=True
            )

        else:

            st.markdown(
                str(content)
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

    # ======================================
    # Display Assistant Response
    # ======================================

    with st.chat_message("assistant"):

        chat_content = response

        if isinstance(response, dict):

            response_type = response.get(
                "type"
            )

            data = response.get(
                "data"
            )

            # ----------------------------------
            # DataFrame
            # ----------------------------------

            if response_type == "dataframe":

                st.dataframe(
                    data,
                    use_container_width=True
                )

                csv = data.to_csv(
                    index=False
                )

                st.download_button(
                    "⬇ Download CSV",
                    csv,
                    file_name="result.csv",
                    mime="text/csv"
                )

                chat_content = data

            # ----------------------------------
            # Series
            # ----------------------------------

            elif response_type == "series":

                st.dataframe(
                    data.to_frame(),
                    use_container_width=True
                )

                chat_content = data

            # ----------------------------------
            # Number
            # ----------------------------------

            elif response_type == "number":

                st.metric(
                    label="Result",
                    value=data
                )

                chat_content = str(data)

            # ----------------------------------
            # Text
            # ----------------------------------

            elif response_type == "text":

                st.markdown(
                    str(data)
                )

                chat_content = str(data)

            # ----------------------------------
            # Error
            # ----------------------------------

            elif response_type == "error":

                st.error(
                    str(data)
                )

                chat_content = (
                    "Error: "
                    + str(data)
                )

            # ----------------------------------
            # Unknown Dict
            # ----------------------------------

            else:

                st.json(response)

                chat_content = str(
                    response
                )

        else:

            if isinstance(
                response,
                pd.DataFrame
            ):

                st.dataframe(
                    response,
                    use_container_width=True
                )

                csv = response.to_csv(
                    index=False
                )

                st.download_button(
                    "⬇ Download CSV",
                    csv,
                    file_name="result.csv",
                    mime="text/csv"
                )

            elif isinstance(
                response,
                pd.Series
            ):

                st.dataframe(
                    response.to_frame(),
                    use_container_width=True
                )

            else:

                st.markdown(
                    str(response)
                )

            chat_content = response

    # ======================================
    # Save Assistant Message
    # ======================================

    st.session_state.messages.append({

        "role": "assistant",

        "content": chat_content
    })