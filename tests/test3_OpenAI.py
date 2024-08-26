
"""
# test3_OpenAI.py
# uses env var OPENAI_API_KEY
"""

from openai import OpenAI

myclient = OpenAI()
mymodel  = "gpt-4-turbo"
myprompt = "Why is the sky blue? Give a short answer"

print(f"asking question '{myprompt}'")
print(f"waiting for response:\n")

resp = myclient.chat.completions.create(
            model=mymodel,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": myprompt}
            ])
ss = resp.choices[0].message.content

print(ss)
print("\nDONE")


