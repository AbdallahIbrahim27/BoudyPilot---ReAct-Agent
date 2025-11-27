import streamlit as st
import os
import requests
import re

# ----------------------
# API Key
# ----------------------
API_KEY = os.getenv("MISTRAL_API_KEY")
BASE_URL = "https://api.mistral.ai/v1/chat/completions"

def call_mistral(prompt, model="mistral-small-latest"):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful reasoning agent."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(BASE_URL, headers=headers, json=payload)
    if response.status_code != 200:
        return f"Error: {response.text}"
    return response.json()["choices"][0]["message"]["content"]

# ----------------------
# Tools
# ----------------------
def search_tool(query):
    return f"[Search Result for '{query}']"

def calculator_tool(expr):
    try:
        return str(eval(expr))
    except:
        return "Error"

TOOLS = {
    "search": search_tool,
    "calculator": calculator_tool
}

# ----------------------
# ReAct Agent
# ----------------------
ACTION_RE = re.compile(r"Action: (\w+)\[(.*?)\]")

def react_agent(query, max_steps=5):
    history = f"User query: {query}\n\n"
    for _ in range(max_steps):
        llm_output = call_mistral(history + "Thought:")
        history += f"Thought: {llm_output}\n"

        action = ACTION_RE.search(llm_output)
        if not action:
            return llm_output

        tool_name, tool_input = action.group(1).lower(), action.group(2)
        observation = TOOLS.get(tool_name, lambda x: "Unknown tool")(tool_input)
        history += f"Observation: {observation}\nResponse: "

    return "Max steps reached."

# ----------------------
# Streamlit UI
# ----------------------
st.title("🧠 Boudy ReAct Agent")

user_input = st.text_input("Enter your query:")

if st.button("Run Agent") and user_input:
    with st.spinner("Thinking..."):
        answer = react_agent(user_input)
        st.success(answer)
