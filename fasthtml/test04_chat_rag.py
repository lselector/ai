
"""
# test04_chat_rag.py
# Example of chatbot using fasthtml and ollama
# Additional modules:
#  - RAG
"""

from fasthtml.common import *
from starlette.requests import Request

import levutils
from levutils.mybag import *
from levutils.myutils import *

import ollama, asyncio

import chromadb

from sentence_transformers import SentenceTransformer

app, rt, = fast_app(live=True, ws_hdr=True)
bag = MyBunch()

client = ollama.Client()
model = "mistral:7b-instruct-v0.3-q4_0"
messages = []

messages_for_show = []

chroma_client = chromadb.Client()

doc_id = 0

bag.script_dir = os.path.dirname(os.path.realpath(__file__))
bag.dir_out = bag.script_dir + "/uploaded_files"

def prepare_db():
    bag.collection = chroma_client.get_or_create_collection(name="my_documents")    


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
            Div("Uploaded files:"),
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
                     )),
                    Div("Uploaded Files:", id="container", 
                    style="width: 300px; height: 200px; background-color: #ced3db"),
                    Form(
                    Input(id='file', name='file', type='file', multiple=True, ondrop="this.form.querySelector('button').click()", 
                          onchange="this.form.querySelector('button').click()"),
                    Button('Upload', type="submit", style="display: none;"),
                    id="upload-form",

                    hx_post="/upload",
                    target_id="container",
                    hx_swap="beforeend",
                    enctype="multipart/form-data"
                ),
            Script(
            """
            const container = document.getElementById('container');
            const fileInput = document.getElementById('file');
            const form = document.getElementById('upload-form');;
            
            container.addEventListener('dragover', (event) => {
                event.preventDefault();
            });

            container.addEventListener('drop', (event) => {
                event.preventDefault();

                //alert("here1");

                const files = event.dataTransfer.files; 

                fileInput.files = files; 

                form.dispatchEvent(new Event('submit')); 
            });
            """
        )
        ))
    )
    
    return main_page

def read_files_from_folder():

    docs = []

    counter = 0

    global doc_id

    for filename in os.listdir(bag.dir_out):
        file_path = os.path.join(bag.dir_out, filename)
        if os.path.isfile(file_path):  
            with open(file_path, 'r') as file:
                
                text = file.read() 

                print(f"name:{filename} File added {text[:100]}, counter: {counter}")
                
                chunks = text.split("\n\n")  # Assuming paragraphs are separated by blank lines

                # 3. Generate Embeddings
                model = SentenceTransformer('all-MiniLM-L6-v2')  # Or your chosen model
                embeddings = model.encode(chunks)

                # 4. Format for Chroma
                
                documents = [
                    {
                        "id": f"doc_{doc_id}",  # Simplified ID
                        "document": chunk,
                        "embedding": embedding.tolist(),
                    }
                    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                ]
                docs.extend(documents)
                doc_id +=1

    return docs

prepare_db()

def do_rag(query):

    try:
        if bag.collection == None:
            return ""
    
    except AttributeError:
        return ""
    
    documents_ = read_files_from_folder()

    counter = 0
    for document in documents_:
       bag.collection.add(ids=[document['id']], documents=[document['document']], embeddings=[document['embedding']])
       print(counter)
       print(document)
       counter+=1
    
    results = bag.collection.query(
        query_texts=[query]
       # n_results=3,  # Adjust as needed
    )
    # all_docs = bag.collection.get()
        
    # if 'documents' in all_docs:
    #     for doc in all_docs['documents']:
    #         print(f"Document debug: {doc}")
    
    return "\n".join([result for result in results['documents'][0]])


@rt('/upload')
async def post(request: Request):
    form = await request.form()
   
    uploaded_files = form.getlist("file")  # Use getlist to get a list of files

    os.makedirs(bag.dir_out, exist_ok=True)

    for uploaded_file in uploaded_files:
        print(f"Uploaded file: {uploaded_file}")

        with open(f"{bag.dir_out}/{uploaded_file.filename}", "wb") as f:
            f.write(uploaded_file.file.read())

    # Update the response to display all uploaded filenames
    return Div(*[P(f"{uploaded_file.filename}") for uploaded_file in uploaded_files]) 
                    

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
 
#---------------------------------------------------------------
@app.ws('/wscon')
async def ws(data:str, send):
    """ Call ollama and get responce using streaming """

    context = do_rag(data)

    messages_for_show.append({"role": "user", "content": f"{data}"})

    messages.append({"role": "user", "content": f"Context: \n {context}, Question: \n {data}"})

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

if __name__ == "__main__":
    uvicorn.run("test04_chat_rag:app", host='localhost', port=5001, reload=True)
