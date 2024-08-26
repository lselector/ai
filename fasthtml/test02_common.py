
"""
# script test02_common.py
# some common elements
"""

# -----------------------------------------
from fasthtml import FastHTML
from fasthtml.common import *

app = FastHTML()

# -----------------------------------------
@app.get("/")
def home():

    mypage = (
        Title("Page Demo"), 
        Div(
            H1('Hello, Lev'), 
            P('Some text'), 
            P(A('LevSelector.com', href='https://LevSelector.com')),
            P(Img(src="https://eais.ai/img/Lev.jpg", width=100, height=100)),
            P(Strong('Some'), I('more text', style="color: #f00;font-size: 30px;")),
            Table(
                Tr(Td("aa"),Td(11)), 
                Tr(Td("bb"),Td(22)),
                Tr(Td("cc"),Td(33))
            )
        )
    )

    return mypage

