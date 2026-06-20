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
    current_files_info = [(f.name, f.size) for f in uploaded_files]
    if st.session_state.get("last_uploaded_files") != current_files_info:
        st.session_state["last_uploaded_files"] = current_files_info
        upload_service = UploadService()
    
        saved_paths = upload_service.save_files(
            uploaded_files
        )
    
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
    
        except Exception as error:
    
            st.error(
                f"Rebuild failed:\n{error}"
            )

if "messages" not in st.session_state or isinstance(st.session_state.messages, list):
    st.session_state.messages = {}
    st.session_state.current_message_id = None
    # View mode: "all" shows the full conversation, "branch" shows a selected branch
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "all"
    if "branch_root_id" not in st.session_state:
        st.session_state.branch_root_id = None
    if "main_leaf_id" not in st.session_state:
        st.session_state.main_leaf_id = None

    # In "all" view we stay here; branch selection is handled by the Branch button per message
    # In "all" view we stay here; branch selection is handled by the Branch button per message


# Determine which messages to display based on view mode
if st.session_state.view_mode == "all":
    # Show the main branch path
    if st.session_state.main_leaf_id:
        display_messages = tree_utils.get_branch_path(st.session_state.messages, st.session_state.main_leaf_id)
    else:
        if st.session_state.messages:
            last_msg = sorted(st.session_state.messages.values(), key=lambda x: x.get("timestamp", ""))[-1]
            st.session_state.main_leaf_id = last_msg["id"]
            if not st.session_state.current_message_id:
                st.session_state.current_message_id = last_msg["id"]
            display_messages = tree_utils.get_branch_path(st.session_state.messages, st.session_state.main_leaf_id)
        else:
            display_messages = []
else:
    # Show only the active path starting from branch_root_id down to current_message_id
    if st.session_state.branch_root_id and st.session_state.current_message_id:
        full_path = tree_utils.get_branch_path(st.session_state.messages, st.session_state.current_message_id)
        try:
            idx = next(i for i, m in enumerate(full_path) if m["id"] == st.session_state.branch_root_id)
            display_messages = full_path[idx:]
        except StopIteration:
            display_messages = [st.session_state.messages[st.session_state.branch_root_id]]
    else:
        display_messages = []

# Render chat messages
for msg in display_messages:
    role = msg["role"]
    is_assistant = (role == "assistant")
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
            
        # Simple navigation buttons (1 and 2)
        if is_assistant:
            col1, col2, _ = st.columns([1, 1, 8])
            is_active_branch_root = (st.session_state.view_mode == "branch" and st.session_state.branch_root_id == msg_id)
            
            with col1:
                if st.session_state.view_mode == "all":
                    st.button("1", key=f"btn1_{msg_id}", disabled=True)
                else:
                    if st.button("1", key=f"btn1_{msg_id}"):
                        st.session_state.view_mode = "all"
                        st.session_state.branch_root_id = None
                        if st.session_state.main_leaf_id:
                            st.session_state.current_message_id = st.session_state.main_leaf_id
                        st.rerun()
            with col2:
                if is_active_branch_root:
                    st.button("2", key=f"btn2_{msg_id}", disabled=True)
                else:
                    if st.button("2", key=f"btn2_{msg_id}"):
                        st.session_state.view_mode = "branch"
                        st.session_state.branch_root_id = msg_id
                        
                        # Smart branch restoration
                        children = tree_utils.get_children(st.session_state.messages, msg_id)
                        if len(children) > 1:
                            leaf = tree_utils.get_leaf_node(st.session_state.messages, children[-1]["id"])
                            st.session_state.current_message_id = leaf
                        else:
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
    if st.session_state.view_mode == "all":
        st.session_state.main_leaf_id = new_user_id

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
    if st.session_state.view_mode == "all":
        st.session_state.main_leaf_id = new_assistant_id

    # Save to history if it's a new successful response
    if history_service and result and result.get("route") != "cached":
        if isinstance(response, dict) and response.get("type") != "error":
            history_service.save_interaction(question, response)
        elif not isinstance(response, dict):
            history_service.save_interaction(question, {"type": "text", "data": str(response)})

    st.rerun()
