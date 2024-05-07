
# --------------------------------------------------------------
# app_flask.py - Flask app - simple chatbot
# uses file templates/index.html
# to run:
#    python app_flask.py
# which starts the local server:
#   http://127.0.0.1:5000
# --------------------------------------------------------------
# pip install flask, openai

import os
from flask import Flask, render_template, request
from openai import OpenAI
client = OpenAI( api_key=os.environ.get("OPENAI_API_KEY") )

app = Flask(__name__)

# --------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# --------------------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form["user_input"]

    response = client.chat.completions.create(
        messages=[ { "role": "user", "content": f"{user_input}", } ],
        model="gpt-3.5-turbo",
    )

    ai_response = response.choices[0].message.content.strip()

    return render_template("index.html",
                           user_input=user_input,
                           ai_response=ai_response)

# --------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
