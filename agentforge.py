"""

"""

import os
import logging
import streamlit as st
from openai import OpenAI


# CONFIG #

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY not set.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)


def log(message):
    logging.info(f"[AgentForge] {message}")


#  VALIDATION #

def validate(output):
    if not output:
        return False
    if "error" in output.lower():
        return False
    return True


# TOOLS #

class Tools:

    @staticmethod
    def calculator(expression):
        try:
            result = eval(expression, {"__builtins__": {}})
            return str(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"


# AGENT  #

class Agent:

    def __init__(self, model):
        self.model = model

    def think(self, task):
        log("Thinking...")

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful AI agent."},
                {"role": "user", "content": task}
            ]
        )

        return response.choices[0].message.content


# ORCHESTRATOR 

class Orchestrator:

    def __init__(self):
        self.agent = Agent(MODEL)

    def execute(self, task):

        log("Executing task")

        if any(char.isdigit() for char in task):
            return Tools.calculator(task)

        result = self.agent.think(task)

        if validate(result):
            log("Result validated")
        else:
            log("Validation failed")

        return result


 STREAMLIT UI

st.set_page_config(page_title="AgentForge", layout="wide")

st.title(" AgentForge - Autonomous AI System")

if "system" not in st.session_state:
    st.session_state.system = Orchestrator()

task = st.text_input("Enter your task:")

if st.button("Execute Task"):
    if not task.strip():
        st.warning("Please enter a task.")
    else:
        with st.spinner("Agent is working..."):
            result = st.session_state.system.execute(task)

        st.success("Execution Complete")
        st.write(result)








