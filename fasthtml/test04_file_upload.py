
"""
# test04_file_upload.py
# FastHTML and htmx do not have any methods to upload files
# We can use any technology to do it
#
# Here is an example using starlette.requests import Request
"""

from fasthtml.common import *
from starlette.requests import Request

app, rt = fast_app()

@rt('/')
def get():
    return Div(
        H1("File Upload"),
            Form(
            Div("Uploaded Files:", id="container", 
                style="width: 300px; height: 200px; background-color: #ced3db"),
            Input(id="new-prompt", type="text", name="data"),
            Label('File', fr='file'),
            Input(id='file', name='file', type='file', multiple=True, ondrop="this.form.querySelector('button').click()", onchange="this.form.querySelector('button').click()"),
            Button('Upload', type="submit", style="display: none;"),
            hx_post="/upload",
            target_id="container",
            hx_swap="beforeend",
            enctype="multipart/form-data"
        ),
        Script(
            """
            const container = document.getElementById('container');
            const fileInput = document.getElementById('file');
            const form = container.closest('form'); 

            container.addEventListener('dragover', (event) => {
                event.preventDefault();
            });

            container.addEventListener('drop', (event) => {
                event.preventDefault();

                const files = event.dataTransfer.files;  

                fileInput.files = files; 

                form.dispatchEvent(new Event('submit')); 
            });
            """
        )
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
