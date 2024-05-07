
# --------------------------------------------------------------
# app_streamlit.py - streamlit app - simple chatbot
# to run:
#    streamlit run app_streamlit.py
# which starts the local server
#   http://localhost:8501/
# --------------------------------------------------------------
# pip install streamlit

import os
import streamlit as st
from openai import OpenAI

client = OpenAI( api_key=os.environ.get("OPENAI_API_KEY") )

st.session_state.messages = []  # chat history

# --------------------------------------------------------------
def generate_response(user_input):

    response = client.chat.completions.create(
        messages=[ { "role": "user", "content": f"{user_input}", } ],
        model="gpt-3.5-turbo",
    )

    return response.choices[0].message.content.strip()

# --------------------------------------------------------------
def main():
    st.title("Streamlit  +  OpenAI gpt-3.5-turbo")

    user_input = st.text_input("Enter your message:")

    if user_input:
        ai_response = generate_response(user_input)

        dict_user = {"role": "user", "content": user_input}
        st.session_state.messages.append(dict_user)

        dict_assistant = {"role": "assistant", "content": ai_response}
        st.session_state.messages.append(dict_assistant)

    for message in st.session_state.messages:
        with st.container():
            st.markdown(f"**{message['role']}:** {message['content']}")

# --------------------------------------------------------------
if __name__ == "__main__":
    main()

