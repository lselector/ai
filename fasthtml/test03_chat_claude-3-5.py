
"""
# test03_chat_claude-3-5.py
# Example of using fastapi + claude-3-5-sonnet
# https://gist.github.com/zhibor/6822d53214892f1c35b2161dc4c5128c
"""

import os, sys, anthropic, asyncio, uvicorn
from fasthtml.common import *

# Set up the app, including daisyui and tailwind for the chat component
tlink = (Script(src="https://unpkg.com/tailwindcss-cdn@3.4.3/tailwindcss.js"),)
dlink = Link(
    rel="stylesheet",
    href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css",
)
app = FastHTML(hdrs=(tlink, dlink, picolink), ws_hdr=True)

sp = {"role": "system", "content": "You are a helpful and concise assistant."}
messages = []

client = anthropic.Anthropic()

myscript = os.path.basename(__file__)
myapp = os.path.splitext(myscript)[0]
print(myapp) 

#---------------------------------------------------------------
def ChatMessage(msg_idx, **kwargs):
    """
    # Chat message component (renders a chat bubble)
    # Now with a unique ID for the content and the message
    """
    msg = messages[msg_idx]
    bubble_class = f"chat-bubble-{'primary' if msg['role'] == 'user' else 'secondary'}"
    chat_class = f"chat-{'end' if msg['role'] == 'user' else 'start'}"
    return Div(
        Div(msg["role"], cls="chat-header"),
        Div(
            msg["content"],
            id=f"chat-content-{msg_idx}",  # Target if updating the content
            cls=f"chat-bubble {bubble_class}",
        ),
        id=f"chat-message-{msg_idx}",  # Target if replacing the whole message
        cls=f"chat {chat_class}",
        **kwargs,
    )

#---------------------------------------------------------------
def ChatInput():
    """
    # The input field for the user message. Also used to clear the
    # input field after sending a message via an OOB swap
    """
    return Input(
        type="text",
        name="msg",
        id="msg-input",
        placeholder="Type a message",
        cls="input input-bordered w-full",
        hx_swap_oob="true",
    )

#---------------------------------------------------------------
@app.route("/")
def get():
    """ The main screen """
    page = Body(
        H1(f"Chatbot Demo: script '{myscript}'"),
        Div(
            *[ChatMessage(msg) for msg in messages],
            id="chatlist",
            cls="chat-box h-[73vh] overflow-y-auto",
        ),
        Form(
            Group(ChatInput(), Button("Send", cls="btn btn-primary")),
            ws_send="",
            hx_ext="ws",
            ws_connect="/wscon",
            cls="flex space-x-2 mt-2",
        ),
        cls="p-4 max-w-lg mx-auto",
    )  # Open a websocket connection on page load
    return Title("Chatbot Demo"), page

#---------------------------------------------------------------
@app.ws("/wscon")
async def ws(msg: str, send):
    """ Call Anthropic Claude LLM """
    msg = msg + ". Respond concisely."
    messages.append({"role": "user", "content": msg})
    # Send the user message to the chat scroller screen
    await send( Div(ChatMessage(len(messages) - 1), hx_swap_oob="beforeend", id="chatlist") )
    await send(ChatInput()) # clear the chat input field
    # ----------------------------------------------------------
    with client.messages.stream(
        max_tokens=1024,
        messages=messages,
        model="claude-3-5-sonnet-20240620"
    ) as stream:
        messages.append({"role": "assistant", "content": ""})
        await send( Div(ChatMessage(len(messages) - 1),
                        hx_swap_oob="beforeend", id="chatlist") )
        for chunk_text in stream.text_stream:
            messages[-1]["content"] += chunk_text
            await send( Span(chunk_text, id=f"chat-content-{len(messages)-1}", hx_swap_oob="beforeend") )
            await asyncio.sleep(0.01)  # simulate a brief delay

#---------------------------------------------------------------
if __name__ == "__main__":
    # serve()
    uvicorn.run(myapp+":app", host="localhost", port=8000, reload=True)
