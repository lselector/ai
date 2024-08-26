
"""
# test05_styles.py
# add external css file in fasthtml
"""

from fasthtml.common import *

css_NotStr = NotStr("<link rel='stylesheet' href='web_app/test.css'>") #works
css_common = Link(rel='stylesheet', href='web_app/test.css')
app, rt = fast_app(pico=False,hdrs=[
    css_common # works
]
)

@rt('/')
def get():
    head = Head(css_common)
    page =  Div(
        #css_NotStr,
        H1("Testing styles"),
            Form(
            Div(id="container", 
                style="width: 300px; height: 200px; background-color: #ced3db"),
            Input(id="new-prompt", type="text", name="data"),
            Label('File', fr='file'),
            Input(id='file', name='file', type='file', multiple=True, ondrop="this.form.querySelector('button').click()", onchange="this.form.querySelector('button').click()"),
            Button('Upload', type="submit", style="display: none;"),
            cls="test-class2",
            
            
            )
        ,cls="test-class"
    )

    return page

serve()
