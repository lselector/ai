
# --------------------------------------------------------------
# app_chainlit.py - simple chatbot
# to run:
#    chainlit run app_chainlit.py
# which starts the local server on port 8000 or 8501 or ...
#   http://localhost:8501/
# --------------------------------------------------------------
# pip install streamlit chainlit
import chainlit as cl
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

openai_model = "gpt-3.5-turbo"

@cl.on_message
async def handle_message(message: cl.Message):
    response = client.chat.completions.create(
        messages = [{"role": "user", "content": message.content}],
        model=openai_model,
        max_tokens=1024,  # Control response length
        n=1,
        stop=None,
        temperature=0.7
    )

    await cl.Message(content=response.choices[0].message.content).send()
