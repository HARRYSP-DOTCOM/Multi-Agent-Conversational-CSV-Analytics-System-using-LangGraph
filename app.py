import streamlit as st
from graphs.analytics_graph import build_graph


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