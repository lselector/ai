
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
            Input(type='file', id='file-upload_', name='files', style="display: none", 
                          onchange="document.getElementById('submit-upload-btn').click()", accept=".txt, .xlsx, .docx, .json, .pdf, .html"),
                    Button('Select Files', cls="select-files-btn", type='button', onclick="document.getElementById('file-upload_').click()"),
                    Button(type="submit", 
                           id="submit-upload-btn", 
                           onclick="createDiv();", 
                           style="display: none",
                           ),
            id="upload-form",
            hx_post="/upload",
            target_id="container",
            hx_swap="beforeend",
            enctype="multipart/form-data"
        ),
        Script(
            """
            const fileInput = document.getElementById('file-upload_');
            const form = document.getElementById('upload-form');;
            
            form.addEventListener('dragover', (event) => {
                event.preventDefault();
            });

            function validateAndSubmit(input) {
                const allowedExtensions = ['.txt', '.xlsx', '.docx', '.json', '.pdf', '.html'];
                const files = input.files;
                const errorMessage = document.getElementById('error-message');

                for (let i = 0; i < files.length; i++) {
                    const file = files[i];
                    const fileExtension = file.name.split('.').pop().toLowerCase();

                    console.log(fileExtension)

                    if (!allowedExtensions.includes('.' + fileExtension)) {
                        errorMessage.style.display = 'block';
                        input.value = ''; 
                        deleteUploadAnimation();
                        return false; // Indicate invalid file type
                    }
                }
                
                return true; // Indicate all files are valid
            }

            form.addEventListener('change', () => {
                event.preventDefault(); 

                createDiv();

                const files = event.dataTransfer.files; 

                fileInput.files = files; 

                form.dispatchEvent(new Event('submit')); 

                });
            """
        ),
    )

@rt('/upload')
async def post(request: Request):
    form = await request.form()
    print("here")
   
    uploaded_files = form.getlist("files")  # Use getlist to get a list of files

    print(f"uploaded_files: {form}")
    uploaded_file = uploaded_files[0]
    print(f"uploaded file: {uploaded_file}")
    
    print(uploaded_file)

    with open(uploaded_file.filename, "wb") as f:
        f.write(uploaded_file.file.read()) 

    # Update the response to display all uploaded filenames
    return Div(*[P(f"{uploaded_file.filename}") for uploaded_file in uploaded_files]) 

serve()
