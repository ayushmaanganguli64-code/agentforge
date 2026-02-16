"""
AGENTFORGE - Autonomous Multi-Agent Workflow System
Hackathon Ready - Single File Version
"""

import os
import logging
import subprocess
import numpy as np
import faiss
import streamlit as st
from openai import OpenAI


# config


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_LARGE = "gpt-4o"
MODEL_SMALL = "gpt-4o-mini"

if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=OPENAI_API_KEY)


# monitoring


logging.basicConfig(level=logging.INFO)

def log(message):
    logging.info(f"[AgentForge] {message}")


# Validator: as antihallucination layer


def validate(output):
    if output is None:
        return False
    if "error" in output.lower():
        return False
    return True


# tool-layer


class Tools:

    @staticmethod
    def calculator(expression):
        try:
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"

    @staticmethod
    def run_code(code):
        try:
            result = subprocess.check_output(
                ["python", "-c", code],
                stderr=subprocess.STDOUT,
                timeout=5
            )
            return result.decode()
        except Exception as e:
            return f"Code execution error: {str(e)}"

    @staticmethod
    def web_lookup(query):
        return f"Simulated web result for: {query}"


# rag memory system (FAISS)


class RAGSystem:

    def __init__(self):
        self.dimension = 1536
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []

    def embed(self, text):
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return np.array(response.data[0].embedding, dtype="float32")

    def add_document(self, text):
        vector = self.embed(text)
        self.index.add(np.array([vector]))
        self.documents.append(text)
        log("Memory stored in FAISS.")

    def search(self, query):
        if len(self.documents) == 0:
            return "No memory available."

        vector = self.embed(query)
        D, I = self.index.search(np.array([vector]), 1)
        idx = I[0][0]

        if idx < len(self.documents):
            log("Memory retrieved from FAISS.")
            return self.documents[idx]

        return "No relevant memory found."

# agents

class BaseAgent:

    def __init__(self, model):
        self.model = model

    def think(self, task, context=""):
        log(f"Agent using model: {self.model}")

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an intelligent autonomous AI agent that reasons step by step."},
                {"role": "user", "content": f"Task: {task}\nContext: {context}"}
            ]
        )

        return response.choices[0].message.content


class ResearchAgent(BaseAgent):
    pass


class MathAgent:
    @staticmethod
    def solve(expression):
        return Tools.calculator(expression)


class CodeAgent:
    @staticmethod
    def execute(code):
        return Tools.run_code(code)


# Mta agent for orchestrator


class Orchestrator:

    def __init__(self):
        self.rag = RAGSystem()
        self.research_agent = ResearchAgent(MODEL_LARGE)

    def choose_model(self, task):
        if any(char.isdigit() for char in task):
            return MODEL_SMALL
        return MODEL_LARGE

    def delegate(self, task):

        log("Analyzing task...")

        if "calculate" in task.lower():
            expression = task.lower().replace("calculate", "")
            return MathAgent.solve(expression)

        elif "code" in task.lower():
            code = task.replace("code", "")
            return CodeAgent.execute(code)

        else:
            context = self.rag.search(task)
            return self.research_agent.think(task, context)

    def execute(self, task):

        log("Starting orchestration")

        result = self.delegate(task)

        if validate(result):
            self.rag.add_document(result)
            log("Result validated & stored in memory.")
        else:
            log("Validation failed.")

        return result


# streamlit-ui


def run_streamlit():

    st.set_page_config(page_title="AgentForge", layout="wide")

    st.title("🚀 AgentForge - Autonomous Multi-Agent System")

    if "system" not in st.session_state:
        st.session_state.system = Orchestrator()

    task = st.text_input("Enter your task:")

    if st.button("Execute Task"):
        with st.spinner("Agents are working..."):
            result = st.session_state.system.execute(task)

        st.success("Execution Complete")
        st.write(result)


# cli mode


def run_cli():

    system = Orchestrator()

    while True:
        task = input("\nEnter Task (or exit): ")

        if task.lower() == "exit":
            break

        output = system.execute(task)

        print("\n=== FINAL OUTPUT ===")
        print(output)


# entry-point


if __name__ == "__main__":

    mode = input("Type 'ui' for Streamlit UI or 'cli' for terminal mode: ").lower()

    if mode == "ui":
        run_streamlit()
    else:
        run_cli()
