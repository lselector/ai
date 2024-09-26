import faiss
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer

# Download the necessary NLTK data files
nltk.download('punkt')

# Step 1: Read the text from a .txt file and chunk it into sentences using NLTK
def read_and_chunk_txt_file(file_path):
    with open(file_path, 'r') as f:
        text = f.read()
    # Chunk the text into sentences using NLTK's sentence tokenizer
    chunks = sent_tokenize(text)
    return chunks

# Step 2: Convert text chunks to vectors using a pre-trained model (Sentence-BERT)
def convert_chunks_to_vectors(chunks, model):
    embeddings = model.encode(chunks)
    return np.array(embeddings).astype('float32')

# Step 3: Initialize FAISS index and add vectors
def create_faiss_index(vectors):
    dimension = vectors.shape[1]  # Dimensionality of the embeddings
    index = faiss.IndexFlatL2(dimension)  # Use L2 distance for search
    index.add(vectors)  # Add vectors to the index
    return index

# Step 4: Perform a search in FAISS index
def search_index(index, query_vector, top_k=5):
    distances, indices = index.search(query_vector, top_k)  # Perform the search
    return distances, indices

# Main function
def main():
    # Path to your .txt file with text content
    file_path = "batman.txt"
    print("starting...")

    # Step 1: Read and chunk the text from the file using NLTK
    text = ""
    with open(file_path, "r") as file:
        text = file.read()

    print("creating sentences...")
    sentences = nltk.sent_tokenize(text)

    print("creating chunks...")
    chunk_size = 3  # Grouping 3 sentences per chunk
    chunks = [' '.join(sentences[i:i+chunk_size]) for i in range(0, len(sentences), chunk_size)]

    print("DONE")
    # Step 2: Convert text chunks into vectors using Sentence-BERT
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Pre-trained model to generate embeddings
    print("creating vectors...")
    
    chunk_embeddings = model.encode(chunks)

    # Step 3: Create FAISS index and add vectors
    print("creating indexes")
    index = create_faiss_index(chunk_embeddings)

    # Example query (using a sample text for the query)
    query_chunk = "tell me about batman"
    query_vector = model.encode([query_chunk]).astype('float32')

    # Step 4: Perform the search
    print("do searching")
    distances, indices = search_index(index, query_vector)

    # Step 5: Print search results with original text chunks as metadata
    print("Search results:")
    for i, idx in enumerate(indices[0]):
        print(f"Match {i+1}: {chunks[idx]} with distance {distances[0][i]}")

if __name__ == "__main__":
    main()
