
"""
# rag_milvus.py
# Example of chatbot using fasthtml and ollama or openai
# Using Milvus as VectorDB
# Additional modules:
#  - RAG
"""

import levutils
from levutils.mybag import *
from levutils.myutils import *
bag = MyBunch()

from fasthtml.common import *
from starlette.requests import Request

import fitz, json, docx, os, nltk
from bs4 import BeautifulSoup
from io import BytesIO
import common_tools as ct

import ollama, asyncio
from openai import OpenAI
from pymilvus import MilvusClient
import pandas as pd

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

client_ollama = ollama.Client()
client_openai = OpenAI()

env_var = os.environ.get('OLLAMA_MODEL')
model = ""
if env_var is None:
    print("Environment variable OLLAMA_MODEL is not set.")
    exit()
else:
   model = env_var

#model = "mistral:7b-instruct-v0.3-q4_0"
#model = "llama3:8b-instruct-q4_0"

messages = []
messages_for_show = []
bag.uploaded_files = []
bag.uploaded_files_to_show_history = []
bag.not_uploaded_files = []
loaded_files_len = 0
m_client = None
isRAG = False
chunks_id = 0
bag.embedding_model = SentenceTransformer('all-MiniLM-L6-v2') 

bag.script_dir = os.path.dirname(os.path.realpath(__file__))
bag.dir_out = bag.script_dir + "/uploaded_files"

sp = {"role": "system", "content": "You are a helpful and concise assistant."}

# ---------------------------------------------------------------
async def init():
    """ Init vectorDB """
    global m_client
    m_client = MilvusClient("./milvus_demo.db")
    m_client.create_collection(
    collection_name="demo_collection",
    dimension=384  # The vectors we will use in this demo has 384 dimensions
    )
    # To preload files in Server. 
    # If you want to have RAG of some default docs
    # await load_file()

# ---------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
   """ Launch when server starts """
   await init()

#---------------------------------------------------------------
@rt('/')
def get():
    """ Main page """
    global bag
    bag.list_items = []
    
    return ct.get_main_page(get_history(), get_uploaded_files_list())

# ---------------------------------------------------------------
def read_files_from_folder(filename, file_path):
    """ Read file from folder and convert it into vectors/chunks """
    docs = []
    if os.path.isfile(file_path):  
        with open(file_path, 'r') as file:
            text = file.read() 
            print(f"name:{filename} File added {text[:100]}")
            chunks = text.split("\n\n") 
            embeddings = bag.embedding_model.encode(chunks)
            documents = [
                {
                    "document": chunk,
                    "embedding": embedding.tolist(),
                    "filename": filename 
                }
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
            ]
            docs.extend(documents)

    return docs

# ---------------------------------------------------------------
def get_data_to_load(documents_, ids_to_reload):
    """ Prepare data for VectorDB insert """
    data = []

    if len(ids_to_reload) == 0:
        data = [{
                    "id": i, 
                    "vector": documents_[i]['embedding'], 
                    "text": documents_[i]['document'], 
                    "filename": documents_[i]['filename'],
                    "year" : "2024",
                    "doc_type" : "upload"
                    } 
                    for i in range(len(documents_)) ]

    else:
        for i in range(len(documents_)):
            data.append({
                        "id": ids_to_reload[i], 
                        "vector": documents_[i]['embedding'], 
                        "text": documents_[i]['document'], 
                        "filename": documents_[i]['filename'],
                        "year" : "2024",
                        "doc_type" : "upload"    
            })

    return data

# ---------------------------------------------------------------
async def load_file(filename, file_path, ids_to_reload):
    """ Load files to VectorDB """
    
    global m_client
    global loaded_files_len
    global isRAG

    documents_ = read_files_from_folder(filename, file_path)
    loaded_files_len = len(documents_)
    print(f"file is loaded! {loaded_files_len}")
    if loaded_files_len > 0:
        isRAG = True
    
    data = get_data_to_load(documents_, ids_to_reload)

    # Assuming 'documents' is a list of dictionaries as in your db example
    res1 = m_client.insert(
    collection_name="demo_collection",
    data=data
    )

# ---------------------------------------------------------------
async def do_rag(query):
    """ Get data from VectorDB """

    global m_client
    res_ = []

    query_vector = bag.embedding_model.encode(query)
    query_vector = np.array([query_vector]) 

    for filename in bag.uploaded_files:
        search_results = m_client.search(
        collection_name="demo_collection",
        data=query_vector,
        filter=f"filename == '{filename}'",  
        output_fields=["text", "filename"],
        limit=5  # Number of top results to return
        )
    
        res_.extend(search_results)
    return res_ 

# ---------------------------------------------------------------
def delete_by_filename(filename):
    """ Delete by filename """

    filename_ = filename.split('.')[0]

    res_ = m_client.query(
        collection_name="demo_collection",
        filter=f"filename == '{filename_}'",
        output_fields=["text", "filename"],
    )

    for _ in range(len(res_)):
        res = m_client.delete( 
        collection_name="demo_collection",
        filter=f"filename == '{filename_}'"
    )

# ---------------------------------------------------------------
async def isFileUploaded(filename):
    """ Check is file upload"""
    try:
        res = m_client.query(
            collection_name="demo_collection",
            filter=f"filename == '{filename}'",
            output_fields=["text", "filename"],
        )

        ids_to_reload = []

        for obj in res:
            ids_to_reload.append(obj['id'])

        if len(ids_to_reload) > 0:
        
            return True, ids_to_reload
        else:
            return False, []
    except:
        return False, []
    
# ---------------------------------------------------------------
async def save_or_reload_file(uploaded_files):
        """ Save or reload uploaded file """
        
        uploaded_files_to_show = []
        not_uploaded_files_to_show = []
        
        for uploaded_file in uploaded_files:

            print(f"Uploaded file: {uploaded_file.filename}")

            file_bytes = await uploaded_file.read()

            file_name = uploaded_file.filename.split('.')[0]
            file_type = uploaded_file.headers.get("content-type") 
            isCorrectType, filename = convert_files(file_bytes, file_name, file_type)

            if not isCorrectType:
                print("Wrong Type!")
                not_uploaded_files_to_show.append(uploaded_file.filename+" is not uploaded")
                bag.not_uploaded_files.append(uploaded_file.filename)
                continue

            is_file_uploaded_, ids_to_reload = await isFileUploaded(filename)

            print(f"is_file_uploaded_:{is_file_uploaded_}")

            if is_file_uploaded_:
                print(f"reloading...{uploaded_file.filename}")
                delete_by_filename(filename)
                
            else:
                print(f"adding...{uploaded_file.filename}")
                bag.uploaded_files.append(filename)
                bag.uploaded_files_to_show_history.append(uploaded_file.filename)
                uploaded_files_to_show.append(uploaded_file.filename)
            
            await load_file(filename,f"{bag.dir_out}/{filename}", ids_to_reload)

        return uploaded_files_to_show, not_uploaded_files_to_show

# ---------------------------------------------------------------
@rt('/upload')
async def post(request: Request):
    """ Upload file(s) from user """

    form = await request.form()
    uploaded_files = form.getlist("files")  # Use getlist to get a list of files
    error_true = Div("Wrong filetype. Allowed only: .txt, .xlsx, .docx, .json, .pdf, .html", hx_swap_oob='true', id="error-message", style="color: red; font-size: 14px;")
    error_false = Div("Wrong filetype. Allowed only: .txt, .xlsx, .docx, .json, .pdf, .html",  hx_swap_oob='true', id="error-message", style="display: none; color: red; font-size: 14px;")
    os.makedirs(bag.dir_out, exist_ok=True)
    print(f"Files to upload: {uploaded_files}")
    uploaded_files_to_show, not_uploaded_files_to_show = await save_or_reload_file(uploaded_files)
    list_items = []

    for uploaded_file in uploaded_files_to_show:
        list_item = Li(f"{uploaded_file}", id='uploaded-file')
        list_items.append(list_item)

    if len(not_uploaded_files_to_show) > 0:
        for not_uploaded_file in not_uploaded_files_to_show:
            list_item = Li(f"{not_uploaded_file}", id='not-uploaded-file', style="color: red")
            list_items.append(list_item) 

        return list_items, error_true
               
    if len(bag.not_uploaded_files) > 0:

        bag.not_uploaded_files = []
        return get_uploaded_files_list(), error_false

    return list_items, error_false

# ---------------------------------------------------------------
@rt('/delete-all-docs')
async def post():
    """ Delete all the data in vectorDB """

    global m_client
    global isRAG

    os.system(f"find {bag.dir_out} -type f -delete")

    m_client.drop_collection("demo_collection")
    m_client.create_collection(
    collection_name="demo_collection",
    dimension=384  # The vectors we will use in this demo has 384 dimensions
    )

    isRAG = False

    bag.uploaded_files = []
    bag.uploaded_files_to_show_history = []

    # Update the response to display all uploaded filenames
    return Ul(id='uploaded-files-list', cls="uploaded-files-list-cls", hx_swap_obb=True)

#---------------------------------------------------------------
def convert_files(file_bytes, file_name, file_type):
    """ Converts different files to txt """
    print(f"Filename: {file_name}, File type: {file_type}")

    if file_type == "text/plain":
        file_name += "__txt.txt"
        read_txt(file_bytes, file_name)
        return True, file_name

    elif file_type == "application/pdf":
        file_name += "__pdf.txt"
        read_pdf(file_bytes, file_name)
        return True, file_name

    elif file_type == "application/json":
        file_name += "__json.txt"
        read_json(file_bytes, file_name)
        return True, file_name
    
    elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        file_name += "__xlsx.txt"
        read_xlsx(file_bytes, file_name)
        return True, file_name
    
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file_name += "__docx.txt"
        read_docx(file_bytes, file_name)
        return True, file_name
    
    elif file_type == "text/html":
        file_name += "__docx.txt"
        read_html(file_bytes, file_name)
        return True, file_name
    
    return False, None

#---------------------------------------------------------------
def read_html(file_bytes,filename):
    """ Read MS Word file """

    soup = BeautifulSoup(BytesIO(file_bytes), 'html.parser')

    # Extract all the text from the HTML
    all_text = soup.get_text(separator='\n')  # Use '\n' as separator for better readability

    write_txt(all_text.strip().encode('utf-8'), filename) 

#---------------------------------------------------------------
def read_docx(file_bytes,filename):
    """ Read MS Word file """

    doc = docx.Document(BytesIO(file_bytes))

    # Extract text from the document
    all_text = ""
    for paragraph in doc.paragraphs:
        all_text += paragraph.text + "\n"

    write_txt(all_text.encode('utf-8'), filename) 

#---------------------------------------------------------------
def read_xlsx(file_bytes,filename):
    """ Read Excel file """

    excel_data = pd.read_excel(BytesIO(file_bytes))

    output = BytesIO()
    excel_data.to_excel(output, index=False)  # Write DataFrame to the BytesIO object
    text_content = excel_data.to_csv(index=False, sep='\t').replace('\t', ' ')  

    #print(text_content)
    write_txt(text_content.encode('utf-8'), filename) 


#---------------------------------------------------------------
def read_json(json_data, filename):
    """ Read JSON file """

    #print(f"Text from json: {json_data}", flush=True) 

    if isinstance(json_data, bytes):
        json_data = json_data.decode('utf-8')
        json_data = json.loads(json_data)  # Now parse the JSON string
    
    text_ = ""

    def extract_text_recursive(data):
        nonlocal text_

        if isinstance(data, dict):
            for value in data.values():
                extract_text_recursive(value)
        elif isinstance(data, list):
            for item in data:
                extract_text_recursive(item)
        elif isinstance(data, str):
            text_ += data + " "  

    extract_text_recursive(json_data)
    write_txt(text_.strip().encode('utf-8'), filename)

#---------------------------------------------------------------
def read_pdf(file_bytes,filename):
    """ Read PDF file """
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:  # Open PDF from bytes
        for page in pdf:
            text += page.get_text()
    
    bytes = text.encode('utf-8') 
    write_txt(bytes, filename)

#---------------------------------------------------------------
def read_txt(file_bytes,filename):
    """ Read txt file """
    write_txt(file_bytes, filename)

#---------------------------------------------------------------
def write_txt(bytes, filename):
    """ Write extracted text to txt file, use file name of original file """
    #bag.write_dir = os.path.dirname(os.path.realpath(__file__))
    write_path = bag.dir_out
    os.makedirs(write_path, exist_ok=True)
    write_path += "/"+filename
    print(f"saving file: {write_path}")
    with open(write_path, "wb") as file:
        file.write(bytes)
                    
#---------------------------------------------------------------
def get_uploaded_files_list():
    """ Get all uploaded files names """ 
    
    lis = []
    for filename in bag.uploaded_files_to_show_history:

        lis.append(
            Li(filename, cls='uploaded-file-cls')
        )

    if len(lis) == 0:
        return Div(Ul(id='uploaded-files-list', cls="uploaded-files-list-cls"), id="files-container", hx_swap_oob='true')

    return Div(Ul(*lis, id='uploaded-files-list', cls="uploaded-files-list-cls"), id="files-container", hx_swap_oob='true')

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
        Div(cls="loading-line", id="loading-line-id"),
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
                if strict == "strict":
                    messages.append({"role": "user", "content": f"Say: In strict mode I answer only using uploaded files. Please appload files"})
                    print("strict+")
                    break
                else:
                    messages.append({"role": "user", "content": f"Question: \n {data}"})
                    print("strict-") 
                    break 
                        
            else:
                if strict == "strict":
                   messages.append({"role": "user", "content": f"Context: \n {context}, Question: \n {data}\n\n Generate your answer only using context. If meaning of the question is not in the context say: \n There is no information about it in the document. If the answer is in history - use history to create answer"})
                   print("strict++")
                   break
                else:
                    messages.append({"role": "user", "content": f"Context: \n {context}, Question: \n {data}answer the question even if it not in the context"})
                    print("strict--")
                    break
                    
    else:
        if strict == "strict":
            messages.append({"role": "user", "content": f"Say: In strict mode I answer only using uploaded files. Please appload files"})
            print("strict+++")
        else:
            messages.append({"role": "user", "content": f"Question: \n {data}answer the question even if it not in the context"})
            print("strict---")  

    if model == "ollama":
        await chat_ollama(send)
    elif model == "openai":
        await chat_openai(send)


# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("rag_milvus:app", host='localhost', port=5001, reload=True)
