
"""
# rag_chromadb.py
# Example of chatbot using fasthtml and ollama or openai
# Using chromadb as VectorDB
# Additional modules:
#  - RAG
"""

from fasthtml.common import *
from starlette.requests import Request

import levutils
from levutils.mybag import *
from levutils.myutils import *

import os
import common_tools as ct

import chromadb

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

collection = None
isRAG = False
chunks_id = 0

# ---------------------------------------------------------------
async def init():
    """ Init vectorDB """
    global m_client
    global collection
    m_client = chromadb.Client()
    collection = m_client.create_collection(name="file_collection")
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
    global chunks_id
    if os.path.isfile(file_path):  
        with open(file_path, 'r') as file:
            text = file.read() 
            print(f"name:{filename} File added {text[:100]}")
            chunks = await ct.split_to_chunks(text)
            embeddings = ct.bag.embedding_model.encode(chunks)
            documents = []
            for _, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                document = {
                    "id": str(chunks_id),
                    "document": chunk,
                    "embedding": embedding.tolist(),
                    "metadata": {
                        "filename": filename,
                        "year": "2024",
                        "doc_type": "upload"
                    }
                }
                chunks_id +=1
                documents.append(document)

            docs.extend(documents)

    return docs

# ---------------------------------------------------------------
def insert_data(documents_, ids_to_reload):
    """ Load files to VectorDB """
    global collection

    if len(ids_to_reload) == 0:
        collection.add(
            documents=[item['document'] for item in documents_],
            embeddings=[item['embedding'] for item in documents_],
            metadatas=[item['metadata'] for item in documents_],
            ids=[item['id'] for item in documents_]
        )
    else:
        collection.add(
            documents=[item['document'] for item in documents_],
            embeddings=[item['embedding'] for item in documents_],
            metadatas=[item['metadata'] for item in documents_],
            ids=[item for item in ids_to_reload]
        )

# ---------------------------------------------------------------
async def load_file(filename, file_path, ids_to_reload, is_file_uploaded_=None):
    """ Get files, set isRAG """
    
    global loaded_files_len
    global isRAG

    documents_ = await read_files_from_folder(filename, file_path)
    loaded_files_len = len(documents_)
    print(f"file is loaded! {loaded_files_len}")

    if loaded_files_len > 0:
        isRAG = True

    insert_data(documents_, ids_to_reload)

# ---------------------------------------------------------------
async def do_rag(query):
    """ Get data from VectorDB """

    global collection
    
    results = collection.query(
        query_texts=[f"{query}"],
        n_results=3
    )
        
    return results 

# ---------------------------------------------------------------
def delete_file(filename):
    """ Delete by filename """

    global collection
    global chunks_id

    res = collection.get(
        where={"filename": f"{filename}"}
    )

    deleted_count = len(res["ids"])

    #print(f"deleting by name: {filename}")
    res_delete = collection.delete(
        where={"filename": f"{filename}"} 
    )

    #deleted_count = len(res_delete['ids'])
    chunks_id -= deleted_count

# ---------------------------------------------------------------
async def isFileUploaded(filename):
    """ Check is file uploaded """
        
    global collection

    res = collection.get(
        where={"filename": f"{filename}"}
    )
    #results = collection.get()
    #print(f"filename {filename}, res: {res}, full: {results}")
    
    if len(res["ids"]) > 0:
        return True, res["ids"]
    else:
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
    global chunks_id
    global collection

    os.system(f"find {ct.bag.dir_out} -type f -delete")

    m_client.delete_collection(name="file_collection")
    collection = m_client.create_collection(name="file_collection")

    isRAG = False

    ct.bag.uploaded_files = []
    ct.bag.uploaded_files_to_show_history = []

    chunks_id = 0

    # Update the response to display all uploaded filenames
    return Ul(id='uploaded-files-list', cls="uploaded-files-list-cls", hx_swap_obb=True), Div("Wrong filetype. Allowed only: .txt, .xlsx, .docx, .json, .pdf, .html",  hx_swap_oob='true', id="error-message", style="display: none; color: red; font-size: 14px;"),
 
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
    uvicorn.run("rag_chromadb:app", host='localhost', port=5001, reload=True)
