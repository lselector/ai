
"""
# test1_ollama.py
"""

import ollama

myclient = ollama.Client()
mymodel  = "llama3.1"
myprompt = "Why is the sky blue? Give a short answer"

print(f"asking question '{myprompt}'")
print(f"waiting for response:\n")

resp = myclient.generate(model=mymodel, prompt=myprompt)
ss = resp['response']
print(ss)
print("\nDONE")
