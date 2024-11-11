
"""
# script test02_count_ws.py
# Simple example how to use WebSockets in fasthtml
"""
import asyncio
from fasthtml import FastHTML
from fasthtml.common import *

app, rt, = fast_app(live=True, ws_hdr=True, exts='ws')
count = 0
# -----------------------------------------
@rt("/")
def get():
    return Title("Count Demo"), Main(
        H1("Count Demo"),
        P(f"Count is set to {count}", id="count-1"),
        Form(
        Button("Increment"),
               ws_send=True, hx_ext="ws", ws_connect="/ws", 
               target_id="count-1", 
               hx_swap="beforeend"
        )
    )
# -----------------------------------------
@app.ws("/ws")
async def ws(send):
    print("incrementing")
    global count
    count += 1
    await send(
        Div(f"Count is set to {count}", hx_swap_oob="true", id="count-1")
        )
# -----------------------------------------
if __name__ == "__main__":
    uvicorn.run("test02_count_ws:app", host='localhost', port=5001, reload=True)
