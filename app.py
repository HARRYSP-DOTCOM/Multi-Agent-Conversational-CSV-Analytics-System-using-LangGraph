import streamlit as st
import pandas as pd
import os
import requests

from graphs.analytics_graph import build_graph
from services.upload_service import UploadService
from services.rebuild_service import RebuildService
from agents.analysis_agent import clear_dataset_cache
from agents.history_agent import history_service
import importlib.util, os, sys
# Ensure utils is on path
utils_path = os.path.join(os.path.dirname(__file__), "utils")
if utils_path not in sys.path:
    sys.path.append(utils_path)
from utils import tree_utils

@st.cache_resource
def get_graph():
    # Force cache invalidation
    return build_graph()

st.markdown(
    """
    <style>
    .stChatMessage[data-role="assistant"] {
        text-align: left;
        margin-right: auto;
    }
    .stChatMessage[data-role="user"] {
        text-align: right;
        margin-left: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("📊 CSV Analytics Agent")

st.write(
    "Upload CSV files and ask questions about your data."
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

    # Removed UI debug messages

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


        # Removed success and info messages from the UI

    except Exception as error:

        st.error(
            f"Rebuild failed:\n{error}"
        )

if "messages" not in st.session_state or isinstance(st.session_state.messages, list):
    st.session_state.messages = {}
    st.session_state.current_message_id = None

active_branch = tree_utils.get_branch_path(st.session_state.messages, st.session_state.current_message_id)

for msg in active_branch:
    role = msg["role"]
    content = msg["content"]
    msg_id = msg["id"]

    with st.chat_message(role):
        if isinstance(content, dict):
            summary = content.get("summary")
            data = content.get("data")
            response_type = content.get("type")
            
            if summary:
                st.markdown(summary)
            
            if response_type == "dataframe":
                st.dataframe(data, use_container_width=True)
            elif response_type == "number":
                st.metric("Result", data)
            elif response_type == "text":
                st.markdown(str(data))
            elif response_type == "error":
                st.error(str(data))
            else:
                st.markdown(str(data))
        else:
            st.markdown(str(content))
            
        # Determine navigation UI components
        nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])
        parent_id = msg.get("parent_id")
        siblings = tree_utils.get_children(st.session_state.messages, parent_id)
        my_children = tree_utils.get_children(st.session_state.messages, msg_id)
        is_tip = (msg_id == st.session_state.current_message_id)
        is_assistant = (role == "assistant")
        has_nav = len(siblings) > 1

        # Parent navigation (if exists)
        if parent_id:
            with nav_col1:
                if st.button("← Parent", key=f"parent_{msg_id}"):
                    st.session_state.current_message_id = parent_id
                    st.rerun()

        # Sibling navigation arrows (only when multiple branches)
        if has_nav:
            idx = next((i for i, s in enumerate(siblings) if s["id"] == msg_id), 0)
            with nav_col2:
                if st.button("←", key=f"prev_{msg_id}", disabled=(idx == 0)):
                    st.session_state.current_message_id = tree_utils.get_leaf_node(st.session_state.messages, siblings[idx-1]["id"])
                    st.rerun()
            with nav_col3:
                st.markdown(f"<div style='text-align: center; margin-top: 10px; font-size: 0.8rem; color: gray;'>{idx+1} / {len(siblings)}</div>", unsafe_allow_html=True)
            with nav_col4:
                if st.button("→", key=f"next_{msg_id}", disabled=(idx == len(siblings)-1)):
                    st.session_state.current_message_id = tree_utils.get_leaf_node(st.session_state.messages, siblings[idx+1]["id"])
                    st.rerun()

        # Branch / Cancel actions (always show Branch for assistants)
        with nav_col5:
            if is_tip and my_children:
                if st.button("Cancel & Go Back", key=f"resume_{msg_id}"):
                    leaf_id = tree_utils.get_leaf_node(st.session_state.messages, my_children[-1]["id"])
                    st.session_state.current_message_id = leaf_id
                    st.rerun()
            if is_assistant:
                if st.button("↳ Branch", key=f"branch_{msg_id}", help="Branch conversation from here"):
                    st.session_state.current_message_id = msg_id
                    st.rerun()


question = st.chat_input(
    "Ask a question..."
)

if question:

    new_user_id = tree_utils.add_message(
        st.session_state.messages,
        role="user",
        content=question,
        parent_id=st.session_state.current_message_id
    )
    st.session_state.current_message_id = new_user_id

    with st.chat_message("user"):

        st.markdown(question)

    try:

        graph = get_graph()

        branch_history = tree_utils.get_branch_path(st.session_state.messages, st.session_state.current_message_id)
        
        initial_state = {
    "question": question,
    "chat_history": branch_history,

    "route": None,
    "route_reason": None,
    "csv_question": None,
    "web_question": None,
    "web_result": None,

    "parsed_query": None,
    "retrieval_result": None,
    "analysis_result": None,

    "final_response": None,

    "generated_code": None,
    "execution_result": None
}

        result = {}
        with st.spinner("Analyzing..."):
            result = graph.invoke(initial_state)

        response = result.get("final_response", {"type": "error", "data": "No response returned"})

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
            
            summary = response.get(
                "summary"
            )
            
            if summary:
                st.markdown(summary)

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

                chat_content = response

            # ----------------------------------
            # Series
            # ----------------------------------

            elif response_type == "series":

                st.dataframe(
                    data.to_frame(),
                    use_container_width=True
                )

                chat_content = response

            # ----------------------------------
            # Number
            # ----------------------------------

            elif response_type == "number":

                st.metric(
                    label="Result",
                    value=data
                )

                chat_content = response

            # ----------------------------------
            # Text
            # ----------------------------------

            elif response_type == "text":
                
                # If we have a summary, we might not want to print raw text unless it's the only thing
                if not summary:
                    st.markdown(
                        str(data)
                    )

                chat_content = response

            # ----------------------------------
            # Error
            # ----------------------------------

            elif response_type == "error":

                st.error(
                    str(data)
                )
            else:
                if not summary:
                    st.json(data)
        else:
            # Render plain text response
            st.markdown(str(response))

    # ======================================
    # Save Assistant Message
    # ======================================

    new_assistant_id = tree_utils.add_message(
        st.session_state.messages,
        role="assistant",
        content=chat_content,
        parent_id=st.session_state.current_message_id
    )
    st.session_state.current_message_id = new_assistant_id

    # Save to history if it's a new successful response
    if history_service and result and result.get("route") != "cached":
        if isinstance(response, dict) and response.get("type") != "error":
            history_service.save_interaction(question, response)
        elif not isinstance(response, dict):
            history_service.save_interaction(question, {"type": "text", "data": str(response)})
