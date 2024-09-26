
"""
# test chromadb
"""

import chromadb
import nltk

from sentence_transformers import SentenceTransformer

nltk.download('punkt')
nltk.download('punkt_tab')

# Create a Chroma client
client = chromadb.Client()

# Create a collection
collection = client.create_collection(name="my_file_collection")

# Specify the file path
file_path = "batman.txt"  # Replace with your actual file path

# Open and read the file
with open(file_path, "r") as file:
    file_contents = file.read()

sentences = nltk.sent_tokenize(file_contents)

chunk_size = 3 
chunks = [' '.join(sentences[i:i+chunk_size]) for i in range(0, len(sentences), chunk_size)] 

# Create a SentenceTransformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2') # Choose an appropriate model

# Create embeddings for each chunk
chunk_embeddings = model.encode(chunks)

metadata = [
    {"source": "batman.txt", "chunk_id": i, "topic": "NLTK Chunking", "year": 2023} # Adjust the year as needed
    for i in range(len(chunks))
]

# Add chunks, embeddings, and metadata to ChromaDB
collection.add(
    documents=chunks,
    embeddings=chunk_embeddings,
    metadatas=metadata,
    ids=[f"chunk_{i}" for i in range(len(chunks))],
)

# Search by "year" metadata
results = collection.query(
    query_texts=["something about NLTK Chunking"],
    n_results=2,
    where={
        "$and": [
            {"year": 2023},
            {"source": "batman.txt"}
        ]
    } 
)

# Print the results
print(results)
