
"""
# rag_multi_models.py
# Example of chatbot using fasthtml and ollama or openai
# Can only read from VectorDB but not upload files
# Using Milvus as VectorDB
# Additional modules:
#  - RAG
"""

from fasthtml.common import *

from mybag import *         # py_utils
from myutils import *       # py_utils 

import ollama, asyncio
from openai import OpenAI
from pymilvus import MilvusClient

from sentence_transformers import SentenceTransformer

app, rt, = fast_app(live=True, ws_hdr=True)
bag = MyBunch()

client_ollama = ollama.Client()
client_openai = OpenAI()
model = "mistral:7b-instruct-v0.3-q4_0"

messages = []
messages_for_show = []
loaded_files_counter = 0
loaded_files_len = 0
m_client = None

bag.script_dir = os.path.dirname(os.path.realpath(__file__))
bag.dir_out = bag.script_dir + "/uploaded_files"

sp = {"role": "system", "content": "You are a helpful and concise assistant."}

# ---------------------------------------------------------------
async def init():
    """ Init vectorDB """
    global m_client
    m_client = MilvusClient("./milvus_demo.db")
    
# ---------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
   """ Launch when server starts """
   await init()

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
                Div(P("Add a message with the form below:"),
                Form(
                    Label("Select model:"),
                    Select(id="shapeInput", name="model")(
                            Option("Ollama", value="ollama", selected=True),
                            Option("OpenAI", value="openai", selected=False)
                           ),
                    Group(
                     Input(id="new-prompt", type="text", name="data"),
                     Button("Submit")
                     ),
                     ws_send=True, hx_ext="ws", ws_connect="/wscon", 
                     target_id='message-list',
                     hx_swap="beforeend",
                     enctype="multipart/form-data",
                     hx_trigger="submit"
                    ),
                    ),
        ))
    )
    
    return main_page

# ---------------------------------------------------------------
async def do_rag(query):
    """ Get data from VectorDB """

    global m_client

    res = m_client.query(
    collection_name="demo_collection",
    filter=f"subject == '{query}'",
    output_fields=["text", "subject"],
    )
    
    model = SentenceTransformer('all-MiniLM-L6-v2') 
    query_vector = model.encode(query)
    query_vector = np.array([query_vector]) 

    search_results = m_client.search(
    collection_name="demo_collection",
    data=query_vector,
    filter="subject == 'superheroes'",  
    output_fields=["text", "subject"],
    #anns_field="superheroes", # Specify the field containing your vectors
    #param={"metric_type": "IP"}, # Or other similarity metric as needed
    limit=5  # Number of top results to return
   
)
    return search_results

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
    for message in messages_for_show:
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

# ---------------------------------------------------------------
async def chat_ollama(send):
    """ Send message to Ollama model """

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

    msg = ""

    # Fill in the message content
    for chunk in stream:
        chunk = chunk["message"]["content"]
        msg = msg + chunk
        messages[-1]["content"] += chunk
        await send(
            Li(chunk, id=tid, hx_swap_oob="beforeend")
        )
        await asyncio.sleep(0.01)  # simulate a brief delay

    messages_for_show.append({"role": "assistant", "content": f"{msg}"})


# ---------------------------------------------------------------
async def chat_openai(send):
    """ Send message to OpenAI model """

    stream = client_openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    stream=True,
)

    messages.append({"role": "assistant", "content": ""})
    await send(
        Div(add_message(""), hx_swap_oob="beforeend", id="message-list")
    )
    
    collected_chunks = []

    i = len(messages)
    tid = f'message-{i}'

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            ss = chunk.choices[0].delta.content
            collected_chunks.append(ss)
            await send(
            Li(ss, id=tid, hx_swap_oob="beforeend")
            )
            await asyncio.sleep(0.01)  # simulate a brief delay

    messages.append({"role": "assistant", "content": ''.join(collected_chunks)})
 
#---------------------------------------------------------------
@app.ws('/wscon')
async def ws(data:str, send, model:str):
    """ Call Ollama or OpenAI and get responce using streaming """
    
    #print(f"{data}, {model}")
   
    context = await do_rag(data)

    messages_for_show.append({"role": "user", "content": f"{data}"})

    messages.append({"role": "user", "content": f"Context: \n {context}, Question: \n {data}"})
  
    await send(
        Div(add_message(data), hx_swap_oob="beforeend", id="message-list")
    )

    # Send the clear input field command to the user
    await send(ChatInput())

    if model == "ollama":
        await chat_ollama(send)
    elif model == "openai":
        await chat_openai(send)

# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("rag_multi_models_read:app", host='localhost', port=5001, reload=True)
