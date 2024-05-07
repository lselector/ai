
"""
# --------------------------------------------------------------
# app_chainlit_ollama.py
# chainlit run app_chainlit_ollama.py
# pip install -U chainlit langchain langchain-community
# --------------------------------------------------------------
"""
import os, sys

from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

from langchain_community.llms import Ollama
from langchain_community.callbacks.tracers.wandb import WandbTracer

import chainlit as cl
# --------------------------------------------------------------
@cl.on_chat_start
async def on_chat_start():

    # Sending an image with the local file path
    elements = [ cl.Image(name="image1", display="inline", path="images/llama3-logo.jpg")  ]
    await cl.Message(content="Hello there, I am Llama3-8b. How can I help you ?", elements=elements).send()
    model = Ollama(model="llama3:latest")
    prompt = ChatPromptTemplate.from_messages( [
            ( "system",
              "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions.",
            ),
            ("human", "{question}"),
    ] )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)

# --------------------------------------------------------------
@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()



