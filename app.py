import streamlit as st
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

    response = (
        "Backend integration "
        "coming next..."
    )

    with st.chat_message("assistant"):

        st.markdown(response)

    st.session_state.messages.append({

        "role": "assistant",

        "content": response
    })