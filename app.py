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

if st.session_state.get("new_edited_question"):
    q_text = st.session_state.new_edited_question["content"]
    p_id = st.session_state.new_edited_question["parent_id"]
    new_user_id = tree_utils.add_message(st.session_state.messages, "user", q_text, p_id)
    st.session_state.current_message_id = new_user_id
    st.session_state.trigger_generation = q_text
    del st.session_state["new_edited_question"]

display_messages = []
if st.session_state.current_message_id:
    display_messages = tree_utils.get_branch_path(st.session_state.messages, st.session_state.current_message_id)
elif st.session_state.messages:
    last_msg = sorted(st.session_state.messages.values(), key=lambda x: x.get("timestamp", ""))[-1]
    st.session_state.current_message_id = last_msg["id"]
    display_messages = tree_utils.get_branch_path(st.session_state.messages, st.session_state.current_message_id)

# Render chat messages
for msg in display_messages:
    role = msg["role"]
    is_assistant = (role == "assistant")
    content = msg["content"]
    msg_id = msg["id"]

    with st.chat_message(role):
        if is_assistant:
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
        else:
            if st.session_state.get(f"editing_{msg_id}", False):
                with st.form(key=f"edit_form_{msg_id}"):
                    new_text = st.text_area("Edit message", value=content, height=100)
                    col1, col2, _ = st.columns([1, 1, 4])
                    with col1:
                        submit = st.form_submit_button("Submit")
                    with col2:
                        cancel = st.form_submit_button("Cancel")
                    
                    if submit:
                        st.session_state[f"editing_{msg_id}"] = False
                        st.session_state.new_edited_question = {
                            "content": new_text,
                            "parent_id": msg.get("parent_id")
                        }
                        st.rerun()
                    if cancel:
                        st.session_state[f"editing_{msg_id}"] = False
                        st.rerun()
            else:
                st.markdown(str(content))
                
                parent_id = msg.get("parent_id")
                if parent_id is None:
                    siblings = [m for m in st.session_state.messages.values() if m.get("parent_id") is None]
                else:
                    siblings = tree_utils.get_children(st.session_state.messages, parent_id)
                
                siblings.sort(key=lambda x: x.get("timestamp", ""))
                
                col1, col2, col3, col4, _ = st.columns([1, 1, 1, 1, 6])
                
                if len(siblings) > 1:
                    idx = siblings.index(msg)
                    with col1:
                        if st.button("◀", key=f"prev_{msg_id}", disabled=(idx == 0)):
                            new_sibling = siblings[idx - 1]
                            st.session_state.current_message_id = tree_utils.get_leaf_node(st.session_state.messages, new_sibling["id"])
                            st.rerun()
                    with col2:
                        st.markdown(f"<div style='padding-top: 5px; text-align: center; font-size: 0.9em;'>{idx + 1}/{len(siblings)}</div>", unsafe_allow_html=True)
                    with col3:
                        if st.button("▶", key=f"next_{msg_id}", disabled=(idx == len(siblings) - 1)):
                            new_sibling = siblings[idx + 1]
                            st.session_state.current_message_id = tree_utils.get_leaf_node(st.session_state.messages, new_sibling["id"])
                            st.rerun()
                    with col4:
                        if st.button("✏️", key=f"edit_btn_{msg_id}"):
                            st.session_state[f"editing_{msg_id}"] = True
                            st.rerun()
                else:
                    with col1:
                        if st.button("✏️", key=f"edit_btn_{msg_id}"):
                            st.session_state[f"editing_{msg_id}"] = True
                            st.rerun()



question = st.chat_input("Ask a question...")

if question:
    new_user_id = tree_utils.add_message(
        st.session_state.messages,
        role="user",
        content=question,
        parent_id=st.session_state.current_message_id
    )
    st.session_state.current_message_id = new_user_id
    st.session_state.trigger_generation = question
    st.rerun()

if st.session_state.get("trigger_generation"):
    q_text = st.session_state.trigger_generation
    del st.session_state["trigger_generation"]

    try:
        graph = get_graph()
        branch_history = tree_utils.get_branch_path(st.session_state.messages, st.session_state.current_message_id)
        
        initial_state = {
            "question": q_text,
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
        result = {}
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
            history_service.save_interaction(q_text, response)
        elif not isinstance(response, dict):
            history_service.save_interaction(q_text, {"type": "text", "data": str(response)})

    st.rerun()
