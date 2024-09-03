

"""
# interactive_diagrams_plumbjs.py
# Using FastHTML and jsPlumb.js to create interactive diagrams

"""

from fasthtml.common import *
from starlette.requests import Request

app, rt = fast_app(live=True)

@rt('/')
def get():
    return Div(
        H1("File Upload")       
    )

@rt('/upload')
async def post(data:str, request: Request):
    form = await request.form()
   
    uploaded_files = form.getlist("file")  # Use getlist to get a list of files

    for uploaded_file in uploaded_files:
        print(f"TEST: {data}")
        
        print(uploaded_file)

        with open(uploaded_file.filename, "wb") as f:
            f.write(uploaded_file.file.read()) 

    # Update the response to display all uploaded filenames
    return Div(P(data),
               *[P(f"{uploaded_file.filename}") for uploaded_file in uploaded_files]) 

serve()
