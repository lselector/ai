
"""
# test6_Claude_stream.py
#
# https://console.anthropic.com - login, create account, add money, 
# generate API key - put it into ANTHROPIC_API_KEY env. variable
#
# https://github.com/anthropics/anthropic-sdk-python
"""

import os, sys, anthropic
client = anthropic.Anthropic()
messages = []

while True:
    print()
    user_message = input("Enter prompt or 'exit' to end > ")
    if user_message.strip().lower() == "exit":
        break
    print()
    messages.append({"role":"user", "content": user_message})

    with client.messages.stream(
        max_tokens=1024,
        messages=messages,
        model="claude-3-5-sonnet-20240620"
    ) as stream:
        response = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            response += text
        print()
    messages.append({"role":"assistant", "content": response})
    print()
