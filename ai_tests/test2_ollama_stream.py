
"""
# test2_ollama_stream.py
"""

import ollama

model_name = 'llama3.1' 

mymodel  = "llama3.1"
myprompt = "Why is the sky blue? Give a concise answer"

print(f"asking question '{myprompt}'")
print(f"waiting for streaming response:\n")

for chunk in ollama.chat(
        model=mymodel, 
        messages=[{'role':'user','content':myprompt}], 
        stream=True
    ):
    print(chunk['message']['content'], end='', flush=True)

print("\nDONE")
