
"""
# rag_faiss.py
# Example of chatbot using fasthtml and ollama or openai
# Using Faiss as VectorDB
# Additional modules:
#  - RAG
"""

from fasthtml.common import *
from starlette.requests import Request

import levutils
from levutils.mybag import *
from levutils.myutils import *

import os

import faiss

import common_tools as ct


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
isTrainned = False

faiss_data_wrapper = []

# ---------------------------------------------------------------
async def init():
    """ Init vectorDB """
    global m_client
    nlist = 5
    quantizer = faiss.IndexFlatL2(384)  # Using L2 distance for the search
    m_client = faiss.IndexIVFFlat(quantizer, 384, nlist)

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

#---------------------------------------------------------------
def get_vectors_ids(chunks, is_file_uploaded, filename, vectors):
    """ Get np array of vectors ids """
    
    global faiss_data_wrapper
    int_vectors_ids = []
    chunks_id = 0
    
    for chunk in chunks:
        int_vectors_ids.append(chunks_id)
        if not is_file_uploaded:
            metadata = {
                    "filename": filename,
                    "year": "2024",
                    "doc_type": "upload"
            }

            new_data = {
                    "chunk": chunk, 
                    "vector_id": chunks_id, 
                    "vector": vectors[chunks_id], 
                    "metadata": metadata
            }

            faiss_data_wrapper.append(new_data)

            chunks_id +=1

    return np.array(int_vectors_ids)

# ---------------------------------------------------------------
async def read_files_from_folder(filename, file_path, is_file_uploaded):
    """ Read file from folder and convert it into vectors/chunks """

    if os.path.isfile(file_path):  
        with open(file_path, 'r') as file:
            text = file.read() 
            print(f"name:{filename} File added {text[:100]}")
            chunks = await ct.split_to_chunks(text)
            vectors = ct.bag.embedding_model.encode(chunks).astype('float32')
            vector_ids = get_vectors_ids(chunks, is_file_uploaded, filename, vectors)

            return vectors, vector_ids

# ---------------------------------------------------------------
async def load_file(filename, file_path, ids_to_reload, is_file_uploaded_):
    """ Load files to VectorDB """
    
    global m_client
    global isRAG
    global isTrainned

    vectors, vectors_ids = await read_files_from_folder(filename, file_path, is_file_uploaded_)

    if len(vectors) > 0:
        isRAG = True

    if isTrainned == False:
        m_client.train(vectors)
        isTrainned == True

    if len(ids_to_reload) == 0:

        # Assuming 'documents' is a list of dictionaries as in your db example
        m_client.add_with_ids(vectors, vectors_ids)
        dimension = vectors.shape[1]
        print(f"dm: {dimension}")
    else:
        m_client.add_with_ids(vectors, ids_to_reload)
        dimension = vectors.shape[1]
        print(f"dm: {dimension}")
        

# ---------------------------------------------------------------
async def do_rag(query):
    """ Get data from VectorDB """

    global m_client
    global faiss_data_wrapper

    res_ = []

    query_vector = ct.bag.embedding_model.encode([query]).astype('float32')

    dimension = query_vector.shape[1]
    print(f"dm: {dimension}")

    distances, indices = m_client.search(query_vector, 5)

    for i, idx in enumerate(indices[0]):
        if idx == -1:  # FAISS returns -1 if no match is found
            continue
        elif faiss_data_wrapper[idx]['metadata']['year'] == "2024":
            res_.append(faiss_data_wrapper[idx]['chunk'])
        
    return res_ 

#---------------------------------------------------------------
def delete_file(ids_to_reload):
    """ Delete file by ids """

    global m_client

    m_client.remove_ids(ids_to_reload)

#---------------------------------------------------------------
async def isFileUploaded(filename):
    """ Is file uploaded """
        
    global faiss_data_wrapper

    chunk_ids = [data['vector_id'] for data in faiss_data_wrapper if data["metadata"]["filename"] == filename]

    if len(chunk_ids) > 0:
        
        return True, np.array(chunk_ids)
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
    global faiss_data_wrapper
    global isTrainned

    os.system(f"find {ct.bag.dir_out} -type f -delete")

    nlist = 5
    quantizer = faiss.IndexFlatL2(384)  # Using L2 distance for the search
    m_client = faiss.IndexIVFFlat(quantizer, 384, nlist)
    isTrainned = False

    isRAG = False

    ct.bag.uploaded_files = []
    ct.bag.uploaded_files_to_show_history = []

    faiss_data_wrapper = []

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
    uvicorn.run("rag_faiss:app", host='localhost', port=5001, reload=True)