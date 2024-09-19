
"""
# test07_hooks_single_button.py
"""
from fasthtml.common import *
from starlette.requests import Request
import datetime as dt
app, rt = fast_app()

# --------------------------------------------------------------
@rt('/')
def get():
    return Body(
    Script("""function do_upload() {
                        const fileInput = document.getElementById("fileInput");
                        const file = fileInput.files[0];
                        alert("do upload file: " + file.name );
                        alert("stop animation");
                }"""),
    Div(
        H1('Test upload hook'),
        Form(
            Input(
                type='file', 
                name='fileInput', 
                id='fileInput',
                hx_post='/upload1', 
                **{'hx-on:htmx:before-request':"alert('Start');"}, 
                **{'hx-on:htmx:after-request':"do_upload();"}, 
                    ),
            Div(id='container'),
            enctype='multipart/form-data',
            hx_swap='textContent',
            hx_target='#container'
        )
    )
)

# --------------------------------------------------------------
@rt('/upload1')
async def post():
    return dt.datetime.now()

# --------------------------------------------------------------
serve()
