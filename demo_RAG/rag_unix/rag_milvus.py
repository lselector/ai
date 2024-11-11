
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

from fasthtml.common import *
from starlette.requests import Request

import os
import common_tools as ct

from pymilvus import MilvusClient


app, rt, = fast_app(live=True, exts='ws', pico=False, ws_hdr=True, hdrs=[
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

m_client = None
isRAG = False

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
    
    return ct.get_main_page()

# ---------------------------------------------------------------
async def read_files_from_folder(filename, file_path):
    """ Read file from folder and convert it into vectors/chunks """
    docs = []
    if os.path.isfile(file_path):  
        with open(file_path, 'r') as file:
            text = file.read() 
            print(f"name:{filename} File added {text[:100]}")
            chunks = await ct.split_to_chunks(text)
            embeddings = ct.bag.embedding_model.encode(chunks)
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
async def load_file(filename, file_path, ids_to_reload, is_file_uploaded_=None):
    """ Load files to VectorDB """
    
    global m_client
    global isRAG

    documents_ = await read_files_from_folder(filename, file_path)
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

    query_vector = ct.bag.embedding_model.encode(query)
    query_vector = np.array([query_vector]) 

    for filename in ct.bag.uploaded_files:
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
def delete_file(filename):
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
@rt('/upload')
async def post(request: Request):
    """ Upload file(s) from user """
    
    list_items, error_false = await ct.upload_file(request, isFileUploaded, load_file, delete_file)

    return list_items, error_false

# ---------------------------------------------------------------
@rt('/delete-all-docs')
async def post():
    """ Delete all the data in vectorDB """

    global m_client
    global isRAG

    os.system(f"find {ct.bag.dir_out} -type f -delete")

    m_client.drop_collection("demo_collection")
    m_client.create_collection(
    collection_name="demo_collection",
    dimension=384  # The vectors we will use in this demo has 384 dimensions
    )

    isRAG = False

    ct.bag.uploaded_files = []
    ct.bag.uploaded_files_to_show_history = []

    # Update the response to display all uploaded filenames
    return Ul(id='uploaded-files-list', cls="uploaded-files-list-cls", hx_swap_obb=True)
                    
 
#---------------------------------------------------------------
@app.ws('/wscon')
async def ws(data:str, send, model:str, strict:str):
    """ Call Ollama or OpenAI and get responce using streaming """
    global isRAG

    await ct.do_chat(data, isRAG, strict, model, send, do_rag=do_rag)

# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("rag_milvus:app", host='localhost', port=5001, reload=True)
