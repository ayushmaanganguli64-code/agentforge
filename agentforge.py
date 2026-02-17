"""

"""

import os
import logging
import streamlit as st
import google.generativeai as genai


#  CONFIG 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not set in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-1.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

logging.basicConfig(level=logging.INFO)


def log(message):
    logging.info(f"[AgentForge] {message}")


#  VALIDATION 

def validate(output):
    if not output:
        return False
    if "error" in output.lower():
        return False
    return True


# TOOLS 

class Tools:

    @staticmethod
    def calculator(expression):
        try:
            
            result = eval(expression, {"__builtins__": {}})
            return str(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"


# AGENT 

class Agent:

    def think(self, task):
        try:
            log("Sending request to Gemini...")
            response = model.generate_content(task)

            if response.text:
                return response.text
            else:
                return "No response generated."

        except Exception as e:
            return f"API Error: {str(e)}"


# ORCHESTRATOR 

class Orchestrator:

    def __init__(self):
        self.agent = Agent()

    def execute(self, task):

        log("Executing task...")

        # Simple math detection
        if any(char.isdigit() for char in task) and any(op in task for op in ["+", "-", "*", "/"]):
            return Tools.calculator(task)

        result = self.agent.think(task)

        if validate(result):
            log("Response validated.")
        else:
            log("Validation failed.")

        return result


#  STREAMLIT UI 

st.set_page_config(page_title="AgentForge", layout="wide")

st.title(" AgentForge - BY ALGORANGERS")

if "system" not in st.session_state:
    st.session_state.system = Orchestrator()

task = st.text_input("Enter your task:")

if st.button("Execute Task"):

    if not task.strip():
        st.warning("Please enter a task.")
    else:
        with st.spinner("Agent is thinking..."):
            result = st.session_state.system.execute(task)

        st.success("Execution Complete")
        st.write(result)
