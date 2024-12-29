
"""
# test5_Claude.py
#
# https://console.anthropic.com - login, create account, add money, 
# generate API key
# put it into ANTHROPIC_API_KEY env. variable
#
# https://github.com/anthropics/anthropic-sdk-python
"""

import anthropic

client = anthropic.Anthropic()  # it gets key from env. variable)

message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Why is the sky blue? Give short answer no longer than 40 words"}
    ]
)

print(message.content[0].text)

