
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
                        alert("do upload");
                        alert("stop animation");
                }"""),
    Div(
        H1('Test upload hook'),
        Form(
            Div(id='container'),
            Button('Start', 
                   hx_post='/upload1', 
                   hx_trigger='click', 
                   **{'hx-on:htmx:before-request':"alert('Start');"}, 
                   **{'hx-on:htmx:after-request':"do_upload();"}, 
                   style='margin-left:10px;'),
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
