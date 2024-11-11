
"""
# test04_ws_demo.py
# https://github.com/AnswerDotAI/fasthtml/blob/main/examples/basic_ws.py
# https://gist.github.com/Mihaiii/d6b6f555781f2cee4c81b9ea1af277d6
"""

from asyncio import sleep
from fasthtml.common import *

app = FastHTML(ws_hdr=True, exts='ws')
rt = app.route
nid = 'notifications'
counter = 0

# --------------------------------------------------------------
def mk_inp(): 
    return Input(id='msg')

# --------------------------------------------------------------
@rt('/')
async def get():
    cts = Div(
        Div(id=nid),
        Form(mk_inp(), 
             id='form', 
             ws_send=True),
             hx_ext='ws', 
             ws_connect='/ws'
             )
    return Titled('Websocket Test', cts)

# --------------------------------------------------------------
async def on_connect(send): 
    await send(Div('Hello, you have connected', id=nid))

# --------------------------------------------------------------
async def on_disconnect( ): 
    print('Disconnected!')

# --------------------------------------------------------------
@app.ws('/ws', conn=on_connect, disconn=on_disconnect)
async def ws(msg:str, send):
    global counter
    await send(Div(f'{counter}: Hello ' + msg, id=nid))
    counter += 1
    await sleep(2)
    return Div('Goodbye ' + msg, id=nid), mk_inp()

# --------------------------------------------------------------
serve()