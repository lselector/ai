
"""
# test4_OpenAI_stream.py
# uses env var OPENAI_API_KEY
"""

from openai import OpenAI

myclient = OpenAI()
mymodel  = "gpt-4o"
myprompt = "Why is the sky blue? Give a short answer"
messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": myprompt}
]

print(f"asking question '{myprompt}'")
print(f"waiting for streaming response:\n")

mystream = myclient.chat.completions.create(
    model=mymodel,
    messages=messages,
    stream=True,
)

for chunk in mystream:
    if chunk.choices[0].delta.content is not None:
            ss = chunk.choices[0].delta.content
            print(ss, end='', flush=True )
print("\nDONE")
