

"""
# interactive_diagrams_plumbjs.py
# Using FastHTML and jsPlumb.js to create interactive diagrams

"""

from fasthtml.common import *
from starlette.requests import Request

app, rt = fast_app(live=True)

@rt('/')
def get():
    return (
        Html(
            Head(
                Meta(charset='UTF-8'),
                Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
                Title('Interactive Flowchart'),
                Script(src='https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js'),
                Script(src='https://cdnjs.cloudflare.com/ajax/libs/jsPlumb/2.15.6/js/jsplumb.min.js'),
                Style('.flowchart-demo {\r\n            width: 800px;\r\n            height: 600px;\r\n            border: 1px solid #ccc;\r\n            position: relative;\r\n        }\r\n        .window {\r\n            width: 150px;\r\n            height: 80px;\r\n            line-height: 80px;\r\n            text-align: center;\r\n            position: absolute;\r\n            background-color: #f0f0f0;\r\n            border: 1px solid #346789;\r\n            border-radius: 4px;\r\n            cursor: move;\r\n            z-index: 10;\r\n        }\r\n        .rectangle { border-radius: 4px; }\r\n        .diamond {\r\n            width: 100px;\r\n            height: 100px;\r\n            transform: rotate(45deg);\r\n            line-height: 100px;\r\n        }\r\n        .diamond span {\r\n            display: inline-block;\r\n            transform: rotate(-45deg);\r\n        }')
            ),
            Body(
                Div(
                    Div('Rectangle', id='window1', style='top:50px;left:50px;', cls='window rectangle'),
                    Div(
                        Span('Diamond'),
                        id='window2',
                        style='top:200px;left:250px;',
                        cls='window diamond'
                    ),
                    Div('Rectangle', id='window3', style='top:350px;left:50px;', cls='window rectangle'),
                    id='flowchart-demo',
                    cls='flowchart-demo'
                ),
                Script('$(document).ready(function() {\r\n            try {\r\n                if (typeof jsPlumb === \'undefined\') {\r\n                    throw new Error(\'jsPlumb is not defined. Library may not have loaded correctly.\');\r\n                }\r\n\r\n                var instance = jsPlumb.getInstance({\r\n                    DragOptions: { cursor: \'pointer\', zIndex: 2000 },\r\n                    ConnectionOverlays: [\r\n                        [ "Arrow", { location: 1, width: 10, length: 10 } ]\r\n                    ],\r\n                    Container: "flowchart-demo"\r\n                });\r\n\r\n                instance.batch(function () {\r\n                    instance.draggable($(".flowchart-demo .window"), { grid: [20, 20] });\r\n\r\n                    instance.connect({\r\n                        source: "window1",\r\n                        target: "window2",\r\n                        anchor: ["Bottom", "Top"],\r\n                        connector: ["Bezier", { curviness: 50 }],\r\n                        paintStyle: { stroke: "#456", strokeWidth: 2 },\r\n                        endpoint: "Dot",\r\n                        endpointStyle: { fill: "#456" },\r\n                    });\r\n\r\n                    instance.connect({\r\n                        source: "window2",\r\n                        target: "window3",\r\n                        anchor: ["Bottom", "Top"],\r\n                        connector: ["Straight"],\r\n                        paintStyle: { stroke: "#456", strokeWidth: 2 },\r\n                        endpoint: "Dot",\r\n                        endpointStyle: { fill: "#456" },\r\n                    });\r\n                });\r\n\r\n                console.log(\'jsPlumb initialization completed successfully.\');\r\n            } catch (error) {\r\n                console.error(\'Error initializing jsPlumb:\', error);\r\n                alert(\'There was an error initializing the flowchart. Please check the console for details.\');\r\n            }\r\n        });')
            ),
            lang='en'
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
