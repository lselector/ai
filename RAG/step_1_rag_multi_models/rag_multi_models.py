
"""
# rag_multi_models.py
# Example of chatbot using fasthtml and ollama or openai
# Using Milvus as VectorDB
# Additional modules:
#  - RAG
"""

from fasthtml.common import *
from starlette.requests import Request

from mybag import *         # py_utils
from myutils import *       # py_utils 

import ollama, asyncio, subprocess
from openai import OpenAI
from pymilvus import MilvusClient

from sentence_transformers import SentenceTransformer

app, rt, = fast_app(live=True, pico=False, ws_hdr=True, hdrs=[
    Link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"
        ), 
    Link(
        rel="stylesheet", 
        href="https://cdn.jsdelivr.net/npm/@picocss/pico@latest/css/pico.min.css"
        ),
    Link(
        rel='stylesheet', 
        href='styles.css'
        )
    
])
bag = MyBunch()

client_ollama = ollama.Client()
client_openai = OpenAI()

#model = "mistral-nemo"

model = "mistral:7b-instruct-v0.3-q4_0"
#model = "llama3:8b-instruct-q4_0"

messages = []
messages_for_show = []
bag.uploaded_files = []
loaded_files_counter = 0
loaded_files_len = 0
m_client = None
isRAG = False
chunks_id = 0

bag.script_dir = os.path.dirname(os.path.realpath(__file__))
bag.dir_out = bag.script_dir + "/uploaded_files"

sp = {"role": "system", "content": "You are a helpful and concise assistant."}

# ---------------------------------------------------------------
async def init():
    """ Init vectorDB """
    global m_client
    m_client = MilvusClient("./milvus_demo.db")
    # To preload files in Server. 
    # If you want to have RAG of some default docs
    # await load_files()
    
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
    main_page = (Title("Document Q&A"),
        Div(
        Div(
        Div( 
            H1("Interactive Document Q&A"),
            Div(
            get_history(),
            cls="history-container"),
            Div(
                Form(
                    Div(
                        Select(id="shapeInput", name="model")(
                            Option("Ollama", value="ollama", selected=True),
                            Option("OpenAI", value="openai", selected=False),
                           id="select-model"), 
                    Label("Strict:", cls='px-2'),
                        Input(type="checkbox", 
                              cls="checkboxer", 
                              value="strict", 
                              name="strict", 
                              data_foo="bar"
                              ),
                    cls="model-strict-container"),
                    Group( 
                     Input(id="new-prompt", type="text", name="data"),
                     Button("Submit", onclick="setScrollFalse()")
                     ),
                     ws_send=True, hx_ext="ws", ws_connect="/wscon", 
                     target_id='message-list',
                     hx_swap="beforeend",
                     enctype="multipart/form-data",
                     hx_trigger="submit"
                    )
                    ),
                    cls="wrapper-chat column",
                    id="wrapper-chat-id"
                    ),
                    Div(
                    Div(
                    Div("Uploaded Files:", cls="text-upload"),
                    Div(
                    Div(
                    get_uploaded_files_list(),
                    id="container", cls="upload-files"),
                    id="upload-container-wrapper"
                    ),
                    Div(
                    Form(
                    Input(type='file', id='file-upload_', name='files', multiple=True, style="display: none", onchange="document.getElementById('submit-upload-btn').click()"),
                    Button('Select Files', cls="select-files-btn", type='button', onclick="document.getElementById('file-upload_').click()"),
                    Button(type="submit", id="submit-upload-btn", style="display: none"),
                    id="upload-form",
                    hx_post="/upload",
                    target_id="uploaded-files-list",
                    hx_swap="innerHTML",
                    enctype="multipart/form-data",
                    cls="upload-cls"
                    ),
                    Form(Group(
                    Button("Clear", type="submit", id="clear-files")
                    ),
                    hx_post="/delete-all-docs",
                    target_id='uploaded-files-list',
                    hx_swap="outerHTML"
                    # cls="upload-button-container"
                    ),
                    cls="forms-container"
                    ),
                    
                
            Script(
            """
            const container = document.getElementById('container');
            const fileInput = document.getElementById('file-upload_');
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

            container.addEventListener('change', () => {
                event.preventDefault(); 

                const files = event.dataTransfer.files; 

                fileInput.files = files; 

                form.dispatchEvent(new Event('submit')); 

                });
            """
        ),
        Script(
            """

            //const messageList = document.getElementById('chatlist');
            //let timeoutId; 

            //const observer = new MutationObserver(() => {
                // Clear any existing timeout
            //    clearTimeout(timeoutId);

                // Set a new timeout to trigger scrolling after 1 second of inactivity
            //    timeoutId = setTimeout(() => {
            //        scrollToBottom(); 
            //    }, 1000);
            //});

            // Start observing the 'message-list' div for changes
            //observer.observe(messageList, { childList: true, subtree: true });

            //function scrollToBottom() {
            //    messageList.scrollTop = messageList.scrollHeight;
            //}

            const messageList = document.getElementById('chatlist');
            let hasScrolled = false;

            const observer = new MutationObserver(() => {
            if (!hasScrolled) {
                smoothScrollToBottom(); 
                hasScrolled = true;
            }
            });

            observer.observe(messageList, { childList: true, subtree: true });

            function smoothScrollToBottom() {
                messageList.scrollTo({
                    top: messageList.scrollHeight,
                    behavior: 'smooth'
                });
                }
            

            function setScrollFalse() {
                hasScrolled = false;
            }
            """
        ),
        Script(
            """ 
            
            """
        ),
        cls="wrapper-uploaded-files-internal",
        id="uploaded-files-internal"
                    ),
                    cls="wrapper-uploaded-files column",

                    ),                             
        cls="wrapper-content"),
        cls="wrapper-main")
    )
    
    return main_page

# ---------------------------------------------------------------
def read_files_from_folder():
    """ Read files from folder and convert them into vectors/chunks """
    docs = []
    global loaded_files_counter

    os.makedirs(bag.dir_out, exist_ok=True) 
    for filename in os.listdir(bag.dir_out):
        file_path = os.path.join(bag.dir_out, filename)
        if os.path.isfile(file_path):  
            with open(file_path, 'r') as file:
                
                text = file.read() 

                print(f"name:{filename} File added {text[:100]}, counter: {loaded_files_counter}")

                loaded_files_counter+=1
                
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
                        "document": chunk,
                        "embedding": embedding.tolist(),
                        "subject": subject  # Add the subject field
                    }
                    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                ]
                docs.extend(documents)

    return docs

def get_chunks(filename):
    #text = text.encode('utf-8')

    file_path = os.path.join(bag.dir_out, filename)
    if os.path.isfile(file_path):  
        with open(file_path, 'r') as file:
            
            text = file.read() 

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
                    "document": chunk,
                    "embedding": embedding.tolist(),
                    "subject": subject  # Add the subject field
                }
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
            ]
    return documents

# ---------------------------------------------------------------
async def reload_files(filename):
    """ Reload files to VectorDB """
    
    global m_client
    global loaded_files_len
    global isRAG

    m_client.create_collection(
    collection_name="demo_collection",
    dimension=384  # The vectors we will use in this demo has 384 dimensions
    )

    documents_ = get_chunks(filename)

    loaded_files_len = len(documents_)

    if loaded_files_len > 0:
        isRAG = True
    
    data = []
    for i in range(len(documents_)):
        data.append({
                "id": i, 
                "vector": documents_[i]['embedding'], 
                "text": documents_[i]['document'], 
                "subject": documents_[i]['subject'],
                "year" : "2024"
                })
                

    res = m_client.query(
                collection_name="demo_collection",
                filter=f"subject == '{documents_[0]['subject']}'",
                output_fields=["text", "subject"],
            )
    #print(res)
    #print("inserting...")
    #print(data) 

    # Assuming 'documents' is a list of dictionaries as in your db example
    res1 = m_client.insert(
    collection_name="demo_collection",
    data=data
)

# ---------------------------------------------------------------
async def load_files():
    """ Load files to VectorDB """
    
    global m_client
    global loaded_files_len
    global isRAG

    m_client.create_collection(
    collection_name="demo_collection",
    dimension=384  # The vectors we will use in this demo has 384 dimensions
    )

    documents_ = read_files_from_folder()

    loaded_files_len = len(documents_)

    if loaded_files_len > 0:
        isRAG = True

    data = [{
              "id": i, 
              "vector": documents_[i]['embedding'], 
              "text": documents_[i]['document'], 
              "subject": documents_[i]['subject'],
              "year" : "2024",
              "doc_type" : "upload"
              } 
              for i in range(len(documents_)) ]

    # Assuming 'documents' is a list of dictionaries as in your db example
    #print("inserting...")
    #print(data)
    res1 = m_client.insert(
    collection_name="demo_collection",
    data=data
)

# ---------------------------------------------------------------
async def do_rag(query):
    """ Get data from VectorDB """

    global m_client
    
    res_ = []
    # for subject in bag.uploaded_files:
    #     res = m_client.query(
    #     collection_name="demo_collection",
    #     filter=f"subject == '{subject}'",
    #     output_fields=["text", "subject"],
    # )
    # res_.extend(res)
    
    model = SentenceTransformer('all-MiniLM-L6-v2') 
    query_vector = model.encode(query)
    query_vector = np.array([query_vector]) 

    
    for subject in bag.uploaded_files:
        search_results = m_client.search(
        collection_name="demo_collection",
        data=query_vector,
        filter=f"subject == '{subject}'",  
        output_fields=["text", "subject"],
        #anns_field="superheroes", # Specify the field containing your vectors
        #param={"metric_type": "IP"}, # Or other similarity metric as needed
        limit=5  # Number of top results to return
    )
        res_.extend(search_results)
    return res_ 

def delete_by_subject(subject):

    res_ = m_client.query(
        collection_name="demo_collection",
        filter=f"subject == '{subject}'",
        output_fields=["text", "subject"],
    )

    for _ in range(len(res_)):
        res = m_client.delete( 
        collection_name="demo_collection",
        filter=f"subject == '{subject}'"
    )

# ---------------------------------------------------------------
@rt('/upload')
async def post(request: Request):
    """ Upload file(s) from user """

    form = await request.form()

    uploaded_files = form.getlist("files")  # Use getlist to get a list of files
    print(form)

    os.makedirs(bag.dir_out, exist_ok=True)

    for uploaded_file in uploaded_files:
        print(f"Uploaded file: {uploaded_file.filename}")

        res = []
        try:
            res = m_client.query(
                collection_name="demo_collection",
                filter=f"subject == '{uploaded_file.filename}'",
                output_fields=["text", "subject"],
            )
            #print(res)
        except:
            pass
            

        if len(res) > 0:
            #print("deleting...")
            delete_by_subject(uploaded_file.filename)
            #print("inserting...")

            #with open(f"{bag.dir_out}/{uploaded_file.filename}", "wb") as f:
            #    f.write(uploaded_file.file.read())

            #await reload_files(uploaded_file.filename)
            continue
            
        if not len(res) > 0:
            print(f"{len(res)} ... adding")
            bag.uploaded_files.append(uploaded_file.filename)

        with open(f"{bag.dir_out}/{uploaded_file.filename}", "wb") as f:
            f.write(uploaded_file.file.read())

    await load_files()

    return [Li(f"{uploaded_file}", id='uploaded-file') for uploaded_file in bag.uploaded_files]

# ---------------------------------------------------------------
@rt('/delete-all-docs')
async def post():
    """ Delete all the data in vectorDB """

    global m_client
    global isRAG
    global loaded_files_counter

    os.system(f"find {bag.dir_out} -type f -delete")

    # a query that retrieves all entities matching filter expressions.

    #for subject in bag.uploaded_files:
    res_ = m_client.query(
        collection_name="demo_collection",
        filter=f"doc_type == 'upload''",
        output_fields=["text", "subject", "year"],
    )
    print(f"DOCS before deletion:\n{res_}")

    # delete ALL files, include preuploaded
    #for _ in range(len(res_)):
    
    #for _ in range(loaded_files_len):
    res = m_client.delete( 
    collection_name="demo_collection",
    filter=f"doc_type == 'upload'"
    )

    #print(res) 

    # a query that retrieves all entities matching filter expressions.
    res = m_client.query(
        collection_name="demo_collection",
        filter=f"doc_type == 'upload'",
        output_fields=["text", "subject"],
    )
    print(f"DOCS after deletion:\n{res}")

    isRAG = False
    loaded_files_counter = 0

    bag.uploaded_files = []

    # Update the response to display all uploaded filenames
    return Div(Ul(id='uploaded-files-list', cls="uploaded-files-list-cls"), id="files-container", hx_swap_obb=True)


# return Div(Div(id="upload-container"), Script(
#             """
#             const container = document.getElementById('upload-container');
#             const fileInput = document.getElementById('file-upload_');
#             const form = document.getElementById('upload-form');;
            
#             container.addEventListener('dragover', (event) => {
#                 event.preventDefault();
#             });

#             container.addEventListener('drop', (event) => {
#                 event.preventDefault();

#                 //alert("here1");

#                 const files = event.dataTransfer.files; 

#                 fileInput.files = files; 

#                 form.dispatchEvent(new Event('submit')); 
#             });

#             container.addEventListener('change', () => {
#                 event.preventDefault(); 

#                 const files = event.dataTransfer.files; 

#                 fileInput.files = files; 

#                 form.dispatchEvent(new Event('submit')); 
#                 //here1

#                 });
#             """,
#             id="upload-script"
#         ),
#     id="upload-container-wrapper", hx_obb_swap="true")

                    
#---------------------------------------------------------------
def get_uploaded_files_list():
    """ Get all uploaded files names """ 
    
    lis = []
    for filename in bag.uploaded_files:

        lis.append(
            Li(filename, cls='uploaded-file-cls')
        )

    #Ul(Li(filename, cls='uploaded-file-cls'), id='uploaded-files-list', cls="uploaded-files-list-cls")

    if len(lis) == 0:
        return Div(Ul(id='uploaded-files-list', cls="uploaded-files-list-cls"), id="files-container", hx_swap_obb=True)

    return Div(Ul(*lis, id='uploaded-files-list', cls="uploaded-files-list-cls"), id="files-container", hx_swap_obb=True)

#---------------------------------------------------------------
def get_history():
    """ Get all history messages """ 
    listed_messages = print_all_messages()
    history = Div(listed_messages, id="chatlist", cls="list-of-messages")

    return history

#---------------------------------------------------------------
def add_message(data, role):
    """ Add message """
    i = len(messages_for_show)
    tid = f'message-{i}'
 
    cls_ = ""

    if role == "end":
        cls_ = "primary"
    elif role =="start":
        cls_ = "secondary"

    list_item = Div(
                Div(data,
                cls=f"chat-bubble chat-bubble-{cls_}",
                id=tid,
                hx_swap_oob="true"
                ),
                cls = f"chat chat-{role}"
                )
    bag.list_items.append(list_item)

    return list_item

#---------------------------------------------------------------
def print_all_messages():
    """ Create ul from messages and return them to main page """
    
    i = 0
    for message in messages_for_show:
        tid = f'message-{i}'

        if message['role'] == "assistant":
            list_item = Div(
                Div(message['content'], id=tid,
                    cls="chat-bubble chat-bubble-secondary"),
                cls = "chat chat-start")
            bag.list_items.append(list_item)  # Add the Li element to the list
        
        elif message['role'] == "user":
            list_item = Div(
                Div(message['content'], id=tid,
                    cls="chat-bubble chat-bubble-primary"),
                cls = "chat chat-end")
            bag.list_items.append(list_item)  # Add the Li element to the list
        
        i +=1
        

    return Div(*bag.list_items, id='message-list')

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

    await send(
        add_message("", "start")
    )

    #await asyncio.sleep(0)

    # Model response (streaming)
    stream = ollama.chat(
        model=model,
        messages=[sp] + messages,
        stream=True,
    )
    
    # Send an empty message with the assistant response
    messages.append({"role": "assistant", "content": ""})

    i = len(messages_for_show)
    tid = f'message-{i}'

    msg = ""

    await send(
                Div(Div(
                    cls="chat-bubble chat-bubble-secondary",
                    id=tid
                    ),
                cls = "chat chat-start",
                hx_swap_oob="outerHTML",
                id=tid+"_"
            )
        )

    # Fill in the message content
    for chunk in stream:
        chunk = chunk["message"]["content"]
        msg = msg + chunk
        messages[-1]["content"] += chunk
        await send(
                Div(
                    chunk,
                    hx_swap_oob="beforeend",
                    cls="chat-bubble chat-bubble-secondary",
                    id=tid
                    )
        )
        await asyncio.sleep(0.01)  # simulate a brief delay

    messages.append({"role": "assistant", "content": ''.join(msg)})
    messages_for_show.append({"role": "assistant", "content": ''.join(msg)})
    

def get_loading():
    """ Send loading animation """
    
    i = len(messages_for_show)
    tid = f'message-{i}'

    loading = Div(
        Div(cls="loading-line"),
        id=tid+"_")

    return loading

# ---------------------------------------------------------------
async def chat_openai(send):
    """ Send message to OpenAI model """

    await send(
        add_message("", "start")
    )

    stream = client_openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    stream=True,
    )

    messages.append({"role": "assistant", "content": ""})
    
    
    collected_chunks = []

    i = len(messages_for_show)
    tid = f'message-{i}'

    await send(
                Div(Div(
                    cls="chat-bubble chat-bubble-secondary",
                    id=tid
                    ),
                cls = "chat chat-start",
                hx_swap_oob="outerHTML",
                id=tid+"_"
            )
        )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            ss = chunk.choices[0].delta.content
            collected_chunks.append(ss)
            await send(
                Div(
                    ss,
                    hx_swap_oob="beforeend",
                    cls="chat-bubble chat-bubble-secondary",
                    id=tid
                    )
        )
            await asyncio.sleep(0.01)  # simulate a brief delay

    messages.append({"role": "assistant", "content": ''.join(collected_chunks)})
    messages_for_show.append({"role": "assistant", "content": ''.join(collected_chunks)})
 
#---------------------------------------------------------------
@app.ws('/wscon')
async def ws(data:str, send, model:str, strict:str):
    """ Call Ollama or OpenAI and get responce using streaming """
    global isRAG

    print(f"isRag: {isRAG}, strict: {strict}")

    await send(
        Div(add_message(data, "end"), hx_swap_oob="beforeend", id="message-list")
    )

    messages_for_show.append({"role": "user", "content": f"{data}"})


    await send(
        Div(get_loading(), hx_swap_oob="beforeend", id="message-list")
    )

     # Send the clear input field command to the user
    await send(ChatInput())

    await asyncio.sleep(0)

    if isRAG:
        context = await do_rag(data)

        print(f"doing rag: {context}")

        for l in context:
            if len(l) == 0:
                messages.append({"role": "user", "content": f"Question: \n {data}"})
                
            else:
                if strict == "strict":
                   messages.append({"role": "user", "content": f"Context: \n {context}, Question: \n {data}\n\n Generate your answer only using context. If meaning of the question is not in the context say: \n There is no information about it in the document"})
                   #print("strict++")
                else:
                    messages.append({"role": "user", "content": f"Context: \n {context}, Question: \n {data}answer the question even if it not in the context"})
                    #print("strict--")
                    
    else:
        messages.append({"role": "user", "content": f"Question: \n {data}"})  

    if model == "ollama":
        await chat_ollama(send)
    elif model == "openai":
        await chat_openai(send)

# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("rag_multi_models:app", host='localhost', port=5001, reload=True)
