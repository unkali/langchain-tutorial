import streamlit as st

from bedrock import translate

st.set_page_config(page_title="Heavy Lifter Demo", page_icon="📈")

st.markdown("# Heavy Lifter Demo")
st.sidebar.header("SQL Query Demo")
st.write(
    """This demo illustrates the use case of querying the database using Natural 
Language input. Based on the input, data is returned in a tabular format or a 
beautiful dashboard. Have fun!"""
)

# Reference doc for chat based UI
# https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask me anything! I will do the heavy lifting for you"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = translate(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
