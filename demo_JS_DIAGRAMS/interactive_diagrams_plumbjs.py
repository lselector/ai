

"""
# interactive_diagrams_plumbjs.py
# Using FastHTML and jsPlumb.js to create interactive diagrams

"""

from fasthtml.common import *
from starlette.requests import Request
import json

app, rt = fast_app(live=True)

@rt('/')
def get():
    return (
        Div(
            Div(
                Title('Interactive Flowchart'),
                Script(src='https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js'),
                Script(src='https://cdnjs.cloudflare.com/ajax/libs/jsPlumb/2.15.6/js/jsplumb.min.js'),
                Style('#flowchart-demo {\r\n            width: 800px;\r\n            height: 600px;\r\n            border: 1px solid #ccc;\r\n            position: relative;\r\n        }\r\n        .window {\r\n            width: 150px;\r\n            height: 80px;\r\n            line-height: 80px;\r\n            text-align: center;\r\n            position: absolute;\r\n            background-color: #f0f0f0;\r\n            border: 1px solid #346789;\r\n            border-radius: 4px;\r\n            cursor: move;\r\n            z-index: 10;\r\n        }\r\n        .rectangle { border-radius: 4px; }\r\n        .diamond {\r\n            width: 100px;\r\n            height: 100px;\r\n            transform: rotate(45deg);\r\n            line-height: 100px;\r\n        }\r\n        .diamond span {\r\n            display: inline-block;\r\n            transform: rotate(-45deg);\r\n        }')
            ),
            Div("Uploaded File:", id="uploaded-file"),
                Form(
                    Input(type='file', id='file-upload_', name='files', style="display: none", 
                          onchange="document.getElementById('submit-upload-btn').click()", accept=".txt, .xlsx, .docx, .json, .pdf, .html"),
                    Button('Select Files', cls="select-files-btn", type='button', onclick="document.getElementById('file-upload_').click()"),
                    Button(type="submit", 
                           id="submit-upload-btn", 
                           style="display: none",
                           ),
                    id="upload-form",
                    hx_post="/upload",
                    target_id="flowchart-demo",
                    hx_swap="outerHTML",
                    enctype="multipart/form-data"
                ),
                Div(id='flowchart-demo'),
        )      
    )

def get_diagram(filename):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    dir_out = script_dir + "/uploaded_diagram3"
    file_path = dir_out + "/" + filename 

    with open(file_path, 'r') as file:
        data = json.load(file)
        return data
    
@rt('/upload')
async def post(request: Request):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    dir_out = script_dir + "/uploaded_diagram3"
    
    form = await request.form()
   
    uploaded_files = form.getlist("files")  # Use getlist to get a list of files

    print(f"uploaded_files: {form}")
    uploaded_file = uploaded_files[0]
    print(f"uploaded file: {uploaded_file}")

    os.makedirs(dir_out, exist_ok=True)

    with open(f"{dir_out}/{uploaded_file.filename}", "wb") as f:
        f.write(uploaded_file.file.read()) 

    # Update the response to display all uploaded filenames
    return Div(
               Script("""
        function createFlowchartElements(instance, diagramData) {
        const flowchartContainer = document.getElementById('flowchart-demo');
                        if (!flowchartContainer) {
            throw new Error('#flowchart-demo container not found.');
        }
        
        // Loop through each element in the JSON
        diagramData.elements.forEach(element => {
            // Create a div element for each flowchart item
            const div = document.createElement('div');       
            div.id = element.id;
            div.className = element.class;
            div.style = element.style;
            div.innerHTML = element.text;
            
            // Append the new element to the container
            flowchartContainer.appendChild(div);
            // Make the element draggable using jsPlumb
            instance.draggable(div);
        });
        }

        // Function to create connections between elements based on the JSON
        function createFlowchartConnections(instance, diagramData) {
        diagramData.elements.forEach(element => {
            element.connections.forEach(conn => {
            instance.connect({
                source: element.id,
                target: conn.target,
                anchor: conn.anchor,
                connector: conn.connector,
                paintStyle: { stroke: "#456", strokeWidth: 2 },
                endpoint: "Dot",
                endpointStyle: { fill: "#456" }
            });
            });
        });
        }

        $(document).ready(function() {
            var diagramData = """ +json.dumps(get_diagram(uploaded_file.filename)) + """;
            
            try {
                if (typeof jsPlumb === 'undefined') {
                    throw new Error('jsPlumb is not defined. Library may not have loaded correctly.');
                }

                var instance = jsPlumb.getInstance({
                    DragOptions: { cursor: 'pointer', zIndex: 2000 },
                    ConnectionOverlays: [
                        ["Arrow", { location: 1, width: 10, length: 10 }]
                    ],
                    Container: "flowchart-demo"
                });

                instance.batch(function () {
                    console.log('creating elements')
                    createFlowchartElements(instance, diagramData);
                    console.log('creating connections')
                    createFlowchartConnections(instance, diagramData);
                });

                console.log('Flowchart loaded successfully.');
            } catch (error) {
                console.error('Error initializing jsPlumb:', error);
                alert('Error initializing the flowchart.');
            }
        });
    """),
    id='flowchart-demo'
    ), Div(f"Uploaded File: {uploaded_file.filename}", id="uploaded-file", hx_swap_oob='true')

serve()
