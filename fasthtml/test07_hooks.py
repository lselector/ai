
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
    <button hx-post="/hook1" style="margin-left:10px;"
        hx-on::before-request="test_method()">
    Start
    </button>
    """
)

custom_btn2 = NotStr(
    """
    <button hx-post="/hook2"
        hx-on::after-request="alert('Finish')">
    Finish
    </button>
    """
)

@rt('/')
def get():
    return Div(
        H1("Test hook"),
            Form(
            Div(id="container"),
            custom_btn1,
            custom_btn2,
            target_id="container",
            hx_swap="textContent"
        ),
        Script(
            """
            function test_method() {
                alert("here!")
            }
            """
        )
    )

@rt('/hook1')
async def post():

    return "Started"


@rt('/hook2')
async def post():

    return "Finished" 

serve()
