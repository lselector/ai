
"""
# test04_chat_rag.py
# Example of chatbot using fasthtml and ollama
# Additional modules:
#  - RAG
"""

from fasthtml.common import *
from starlette.requests import Request

from mybag import *         # py_utils
from myutils import *       # py_utils 

import ollama, asyncio

app, rt, = fast_app(live=True, ws_hdr=True)
bag = MyBunch()

client = ollama.Client()
model = "mistral:7b-instruct-v0.3-q4_0"
messages = []

sp = {"role": "system", "content": "You are a helpful and concise assistant."}

#---------------------------------------------------------------
@rt('/')
def get():
    """ Main page """
    bag.list_items = []
    main_page = (
        Title("Chatbot"),
        Titled('Greeting',
        Div(
            H1("Chatbot using fasthtml and ollama"),
            Div(
            P(Img(src="https://fastht.ml/assets/logo.svg", width=100, height=100)),
            ),
            A("About us", href="/about"),
            get_history(),
            Div("Uploaded files:",
                Ul(id="file-upload")),
                Form(
                    Input(id='file', name='file', type='file', onchange="this.form.querySelector('button').click()"),
                    Button('Upload', type="submit", style="display: none;"),
                    hx_post="/upload",
                    target_id="file-upload",
                    hx_swap="beforeend",
                    enctype="multipart/form-data"
                ),
                Div(P("Add a message with the form below:"),
                Form(Group(
                     Input(id="new-prompt", type="text", name="data"),
                     #Input(id="file-upload", type="file", name="file", accept=".txt", method="post", action="/upload"),
                     Button("Submit")
                     ),
                     ws_send=True, hx_ext="ws", ws_connect="/wscon", 
                     target_id='message-list',
                     hx_swap="beforeend",
                     enctype="multipart/form-data"
                     ))
        ))
    )
    
    return main_page


#---------------------------------------------------------------
@rt('/upload')
async def post(request: Request):
    """ upload files """
    form = await request.form()
    uploaded_file = form["file"]
    
    print(uploaded_file)

    bag.script_dir = os.path.dirname(os.path.realpath(__file__))
    bag.dir_out = bag.script_dir + "/uploaded_files"

    os.makedirs(bag.dir_out, exist_ok=True)

    with open(f"{bag.dir_out}/{uploaded_file.filename}", "wb") as f:
        f.write(uploaded_file.file.read())
    
    return Li(f"{uploaded_file.filename}"),
                    

#---------------------------------------------------------------
def get_history():
    """ Get all history messages """
    listed_messages = print_all_messages()
    history = Div(listed_messages, id="chatlist")

    return history

#---------------------------------------------------------------
def add_message(data):
    """ Add message """
    i = len(messages)
    tid = f'message-{i}'
    
    list_item = Li(data,
                id=tid)
    bag.list_items.append(list_item)

    return list_item

#---------------------------------------------------------------
def print_all_messages():
    """ Create ul from messages and return them to main page """
    
    i = 0
    for message in messages:
        tid = f'message-{i}'
                 
        list_item = Li(message['content'],
                       id=tid)  # Create an Li element for each message
        bag.list_items.append(list_item)  # Add the Li element to the list
        i +=1

    return Ul(*bag.list_items, id='message-list')

#---------------------------------------------------------------
@rt('/about')
def get():
    """ second page """
    main_page = (
        Titled('About us',
        Div(
            H1("How Chatbot works:"),
            Div(
            P(Img(src="https://fastht.ml/assets/logo.svg", width=100, height=100)),
            ),
            P("Hi!"),
            A("Home page", href="/"),
        ))
    )

    return main_page

#---------------------------------------------------------------
def ChatInput():
    """ Clear the input """
    return Input(id="new-prompt", type="text", name='data',
                 placeholder="Type a message",
                 cls="input input-bordered w-full", hx_swap_oob='true')
 
#---------------------------------------------------------------
@app.ws('/wscon')
async def ws(data:str, send):
    """ Call ollama and get responce using streaming """

    messages.append({"role": "user", "content": data})

    await send(
        Div(add_message(data), hx_swap_oob="beforeend", id="message-list")
    )

    # Send the clear input field command to the user
    await send(ChatInput())

    # Model response (streaming)
    stream = ollama.chat(
        model=model,
        messages=[sp] + messages,
        stream=True,
    )

    # Send an empty message with the assistant response
    messages.append({"role": "assistant", "content": ""})
    await send(
        Div(add_message(""), hx_swap_oob="beforeend", id="message-list")
    )

    i = len(messages)
    tid = f'message-{i}'

    # Fill in the message content
    for chunk in stream:
        chunk = chunk["message"]["content"]
        messages[-1]["content"] += chunk
        await send(
            Li(chunk, id=tid, hx_swap_oob="beforeend")
        )
        await asyncio.sleep(0.01)  # simulate a brief delay

if __name__ == "__main__":
    uvicorn.run("test04_chat_rag:app", host='localhost', port=5001, reload=True)
