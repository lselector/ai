
# --------------------------------------------------------------
# app_streamlit_cookies.py - streamlit app - simple chatbot with history memory
# 
# NOT WORKING YET
# 
# uses cookies to store info between submissions
# https://pypi.org/project/extra-streamlit-components/
# https://discuss.streamlit.io/t/streamlit-cookies-which-package-to-use-so-many-of-them/50500
# 
# to run:
#    streamlit run app_streamlit_cookies.py
# which starts the local server
#   http://localhost:8501/
# --------------------------------------------------------------
# pip install streamlit

import os, json
import streamlit as st
from openai import OpenAI

client = OpenAI( api_key=os.environ.get("OPENAI_API_KEY") )

st.session_state.messages = []  # chat history
cookie_name = "chat_history"

# --------------------------------------------------------------
def generate_response(prompt):

    response = client.chat.completions.create(
        messages=[ { "role": "user", "content": f"{prompt}", } ],
        model="gpt-3.5-turbo",
    )

    return response.choices[0].message.content.strip()

# --------------------------------------------------------------
def build_prompt(user_input, mes):
    prompt = ""
    for message in mes:
        if message["role"] == "user":
            prompt += f"Human: {message['content']}\n"
        else:
            prompt += f"AI: {message['content']}\n"
    prompt += f"Human: {user_input}\nAI: "  # Append latest user input
    return prompt

# --------------------------------------------------------------
def main():
    # Restore chat history from cookie
    # chat_history = json.loads(st.experimental_get_cookie(cookie_name, "{}"))
    # st.session_state.messages = chat_history

    st.title("Chatbot with memory")

    user_input = st.text_input("Enter your message:")

    if user_input:
        prompt = build_prompt(user_input, st.session_state.messages)
        ai_response = generate_response(prompt)

        dict_user = {"role": "user", "content": user_input}
        st.session_state.messages.append(dict_user)

        dict_assistant = {"role": "assistant", "content": ai_response}
        st.session_state.messages.append(dict_assistant)

#         chat_history = st.session_state.messages
#         st.experimental_set_cookie(cookie_name, json.dumps(chat_history))

    with st.container():
        nn = len(st.session_state.messages)
        st.markdown(f"{nn}")
        for message in st.session_state.messages:
            st.markdown(f"**{message['role']}:** {message['content']}")

# --------------------------------------------------------------
if __name__ == "__main__":
    main()

