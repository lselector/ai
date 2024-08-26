
"""
# script test01_hello.py
"""

from fasthtml import FastHTML
from fasthtml.common import *

app = FastHTML()

# -----------------------------------------
@app.get("/")
def home():
    return "<h1>Hello, World</h1>"
# -----------------------------------------

serve()
