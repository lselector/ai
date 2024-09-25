
"""
# upload_files.py
# external python script to upload/delete files into VectorDB
"""

import os

import levutils
from levutils.mybag import *
from levutils.myutils import *

from pymilvus import MilvusClient

from sentence_transformers import SentenceTransformer

bag = MyBunch()

bag.script_dir = os.path.dirname(os.path.realpath(__file__))
bag.dir_out = bag.script_dir + "/uploaded_files"

loaded_files_counter = 0
loaded_files_len = 0

m_client = MilvusClient("./milvus_demo.db")

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


# ---------------------------------------------------------------
def load_files():
    """ Load files to VectorDB """
    
    global m_client
    global loaded_files_len
    global isRAG

    m_client.create_collection(
    collection_name="demo_collection",
    dimension=384  # The vectors we will use in this demo has 384 dimensions
    )

    if loaded_files_len > 0:
        isRAG = True

    documents_ = read_files_from_folder()

    loaded_files_len = len(documents_)

    data = [{
              "id": i, 
              "vector": documents_[i]['embedding'], 
              "text": documents_[i]['document'], 
              "subject": "superheroes",
              "year" : "2024"
              } 
              for i in range(len(documents_)) ]

    # Assuming 'documents' is a list of dictionaries as in your db example
    res1 = m_client.insert(
    collection_name="demo_collection",
    data=data
)
    

# ---------------------------------------------------------------
def delete_all_files():
    """ Delete all the data in vectorDB """

    global m_client
    global isRAG

    loaded_files_len = 0

    # a query that retrieves all entities matching filter expressions.
    res = m_client.query(
        collection_name="demo_collection",
        filter="subject == 'superheroes' and year == '2024'",
        output_fields=["text", "subject", "year"],
    )
    print(f"DOCS before deletion:\n{res}")

    for _ in res:
        loaded_files_len +=1

    #for _ in range(loaded_files_len):
    res = m_client.delete( 
    collection_name="demo_collection",
    filter="subject == 'superheroes'"
    )
    print(f"TEST: {res}")

    # a query that retrieves all entities matching filter expressions.
    res = m_client.query(
        collection_name="demo_collection",
        filter="subject == 'superheroes'",
        output_fields=["text", "subject"],
    )
    print(f"DOCS after deletion:\n{res}")

    isRAG = False
                    
#load_files()
delete_all_files() # Do not works when server running
