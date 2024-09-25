
"""
# test04_chat_rag_milvus.py
# Example of chatbot using fasthtml and ollama
# Using Milvus as VectorDB
# Additional modules:
#  - RAG
"""

from fasthtml.common import *
from starlette.requests import Request

import levutils
from levutils.mybag import *
from levutils.myutils import *

import ollama, asyncio
from pymilvus import MilvusClient

from sentence_transformers import SentenceTransformer

app, rt, = fast_app(live=True, ws_hdr=True)
bag = MyBunch()

client = ollama.Client()
model = "mistral:7b-instruct-v0.3-q4_0"
messages = []

messages_for_show = []

doc_id = 0

m_client = None

async def init():
    global m_client
    m_client = MilvusClient("./milvus_demo.db")
    await load_files()

@app.on_event("startup")
async def startup_event():
    await init()

bag.script_dir = os.path.dirname(os.path.realpath(__file__))
bag.dir_out = bag.script_dir + "/uploaded_files"


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

def read_files_from_folder2():
    docs = []
    counter = 0
    global doc_id

    for filename in os.listdir(bag.dir_out):
        file_path = os.path.join(bag.dir_out, filename)
        if os.path.isfile(file_path):  
            with open(file_path, 'r') as file:
                
                text = file.read() 

                print(f"name:{filename} File added {text[:100]}, counter: {counter}")
                
                chunks = text.split("\n\n") 

                # 3. Generate Embeddings
                model = SentenceTransformer('all-MiniLM-L6-v2') 
                embeddings = model.encode(chunks)

                # 4. Format for db, including 'subject' field
                # You'll need to determine the subject for each file. 
                # Here, I'm just using the filename as a placeholder. 
                # You might need more sophisticated logic to extract the subject from the file content.
                subject = filename  # Replace with your actual subject extraction logic

                documents = [
                    {
                        "id": doc_id,
                        "document": chunk,
                        "embedding": embedding.tolist(),
                        "subject": subject  # Add the subject field
                    }
                    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                ]
                docs.extend(documents)
                doc_id +=1

    return docs

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

                # 4. Format for db
                
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

#prepare_db()

async def load_files():
    global m_client
    m_client.create_collection(
    collection_name="demo_collection",
    dimension=384  # The vectors we will use in this demo has 384 dimensions
    )

    documents_ = read_files_from_folder2()

    from tqdm import tqdm

    # data = []

    # for i, line in enumerate(tqdm(documents_['document'], desc="Creating embeddings")):
    #     data.append({"id": i, "vector": documents_['embeddings'], "text": line})

    #vectors = [[ np.random.uniform(-1, 1) for _ in range(384) ] for _ in range(len(docs)) ]
    #print(f"TEST: {documents_[0]['embedding']}")
    data = [ {"id": i, "vector": documents_[i]['embedding'], "text": documents_[i]['document'], "subject": "superheroes"} for i in range(len(documents_)) ]

    # Assuming 'documents' is a list of dictionaries as in your db example
    res1 = m_client.insert(
    collection_name="demo_collection",
    data=data
)

async def do_rag(query):
    global m_client
    await load_files()

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
    #context = ""
    context = await do_rag(data)

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
    uvicorn.run("test04_chat_rag_milvus:app", host='localhost', port=5001, reload=True)
