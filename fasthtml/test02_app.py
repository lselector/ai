
"""
# script test02_app.py
"""
from fasthtml import FastHTML
from fasthtml.common import *

app = FastHTML()

messages = ["messages rendered as paragraphs"]

# -----------------------------------------
def calc_home():
    ss = Main(
        H1('Messages'), 
        *[P(msg) for msg in messages],
        A("Link to Page 2 (to add messages)", href="/page2")
    )
    print("1"*60)
    print(type(ss))
    print("2"*60)
    print(to_xml(ss))
    print("3"*60)
    return ss

# -----------------------------------------
@app.get("/")
def home():
    return calc_home()
# -----------------------------------------
@app.post("/")
def add_message(data:str):
    messages.append(data)
    print(f"adding message {data}")
    #     return RedirectResponse(url="/")
    #     return RedirectResponse(url="http://localhost:5001")
    #     return home
    #     return home()
    return calc_home()
# -----------------------------------------
@app.get("/page2")
def page2():
    return Main(
  P("Add a message with the form below:"),
  Form( Input(type="text", name="data"),
        Button("Submit"),
        action="/", method="post"))
# -----------------------------------------

serve()