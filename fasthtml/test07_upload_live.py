
"""
# test04_file_upload.py
# FastHTML and htmx do not have any methods to upload files
# We can use any technology to do it
#
# Here is an example using starlette.requests import Request
"""

from fasthtml.common import *
from starlette.requests import Request
import time

app, rt = fast_app()

custom_btn1 = NotStr(
    """
    <Input id='file' name='file' type='file' multiple=True onchange="this.form.querySelector('button').click()"
        
    Start

    <Button type="submit" 
    hx-post="/upload"
    hx-on::before-request="alert('Start')"
    hx-on::after-request="alert('Finish')"
    style="margin-left:10px;" style="display: none;"></Button>
    </Input>
    """
)


@rt('/')
def get():
    return Div(
        H1("File Upload"),
            Form(
            Div("Uploaded Files:", id="container", 
                style="width: 300px; height: 200px; background-color: #ced3db"),
            Input(id="new-prompt", type="text", name="data"),
            Label('File', fr='file'),
            #Input(id='file', name='file', type='file', multiple=True, ondrop="this.form.querySelector('button').click()", onchange="this.form.querySelector('button').click()"),
            #Button('Upload', type="submit", style="display: none;"),
            custom_btn1,
            #hx_post="/upload",
            target_id="container",
            hx_swap="beforeend",
            enctype="multipart/form-data"
        )
    )

@rt('/upload')
async def post(request: Request):
    form = await request.form()
   
    uploaded_files = form.getlist("file")  # Use getlist to get a list of files

    for uploaded_file in uploaded_files:
        
        print(uploaded_file)

        with open(uploaded_file.filename, "wb") as f:
            f.write(uploaded_file.file.read()) 

    # Update the response to display all uploaded filenames
    return Div(
               *[P(f"{uploaded_file.filename}") for uploaded_file in uploaded_files]) 

serve()
