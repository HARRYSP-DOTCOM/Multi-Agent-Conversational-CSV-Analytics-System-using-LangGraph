import streamlit as st
#from graphs.analytics_graph import build_graph
st.set_page_config(
    page_title="CSV Analytics Agent",
    page_icon="📊",
    layout="wide"
)
st.title("📊 CSV Analytics Agent")
st.write(
    "Ask questions about your uploaded datasets."
)
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


question = st.chat_input(
    "Ask a question..."
)


if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    try:

        response = (
            "Streamlit backend connected successfully."
        )

    except Exception as error:

        response = f"Error: {error}"

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })