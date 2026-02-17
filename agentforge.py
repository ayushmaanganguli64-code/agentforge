"""

"""

import streamlit as st
from google import genai

# Page setup
st.set_page_config(page_title="Gemini Chat App", page_icon="🤖")
st.title("ALGORANGER's MODEL")

# Check if API key exists
if "GEMINI_API_KEY" not in st.secrets:
    st.error(" GEMINI_API_KEY not found in Streamlit Secrets.")
    st.stop()

# Initialize Gemini client
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f" Failed to initialize Gemini client: {e}")
    st.stop()

# Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Ask me anything...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_input
        )

        bot_reply = response.text

    except Exception as e:
        st.error(f" API ERROR: {e}")
        st.stop()

    # Save and display response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
