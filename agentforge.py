"""

"""

import streamlit as st
from google import genai

# Page config
st.set_page_config(page_title="Gemini Chat App", page_icon="🤖")

st.title(" ALGORANGERS-MODEL")

# Load API key 
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize 
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Ask something...")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=user_input
    )

    bot_reply = response.text

    # Save
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
