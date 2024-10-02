

"""
# interactive_diagrams_cytoscape.py
# Using FastHTML and Cytoscape.js to create interactive diagrams

"""

from fasthtml.common import *
from starlette.requests import Request

import json

app, rt = fast_app(live=True)

@rt('/')
def get():
    return (
        Html(
            Head(
                Meta(charset='UTF-8'),
                Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
                Title('Cytoscape.js Interactive Flowchart'),
                #  Form(
                #     Label("Shape:", for_="shapeInput"),
                #     Select(
                #             Option("Rectangle", value="rectangle"),
                #             Option("Diamond", value="diamond"),
                #             id="shapeInput"
                #            ),
                #     Br(),
                #     Label("Label:", for_="labelInput"),
                #     Input(id="labelInput", type="text"),
                #     Br(),
                #     Label("X Position:", for_="xInput"),
                #     Input(id="xInput", type="number", value="200"),
                #     Br(),
                #     Label("Y Position:", for_="yInput"),
                #     Input(id="yInput", type="number", value="200"),
                #     Br(),
                #     Button("Add Shape", type="button", onclick="addShape()"),
                # ),
                Div(id='uploaded-file'),
                Div("Uploaded Files:", id="container", 
                style="width: 300px; height: 200px; background-color: #ced3db"),
                Form(
                    Input(type='file', id='file-upload_', name='files', multiple=True, style="display: none", 
                          onchange="document.getElementById('submit-upload-btn').click()", accept=".txt, .xlsx, .docx, .json, .pdf, .html"),
                    Button('Select Files', cls="select-files-btn", type='button', onclick="document.getElementById('file-upload_').click()"),
                    Button(type="submit", 
                           id="submit-upload-btn", 
                           style="display: none",
                           ),
                    #**{'hx-on:htmx:after-request':"deleteUploadAnimation();"},
                    id="upload-form",
                    hx_post="/upload",
                    target_id="uploaded-file",
                    hx_swap="outerHTML",
                    enctype="multipart/form-data",
                    cls="upload-cls",
                ),
                Script(src='https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.23.0/cytoscape.min.js'),
                Style('#flowchart-demo {\r\n            width: 800px;\r\n            height: 600px;\r\n            border: 1px solid #ccc;\r\n        }'),
            
            ),
            Body(
                Div(id='flowchart-demo'),
                Script(
                    """
                    document.addEventListener('DOMContentLoaded', function() {
                        var cy = cytoscape({
                            container: document.getElementById('flowchart-demo'),
                            elements: """ + json.dumps(generate_elements()) + """,
                            style: [
                                {
                                    selector: 'node',
                                    style: {
                                        'background-color': '#f0f0f0',
                                        'border-color': '#346789',
                                        'border-width': 1,
                                        'label': 'data(label)',
                                        'text-valign': 'center',
                                        'text-halign': 'center',
                                        'width': 150,
                                        'height': 80
                                    }
                                },
                                {
                                    selector: 'node[id="diamond"]',
                                    style: {
                                        'shape': 'diamond',
                                        'width': 100,
                                        'height': 100
                                    }
                                },
                                {
                                    selector: 'edge',
                                    style: {
                                        'width': 2,
                                        'line-color': '#999',
                                        'target-arrow-color': '#999',
                                        'target-arrow-shape': 'triangle',
                                        'curve-style': 'bezier'
                                    }
                                }
                            ],
                            layout: {
                                name: 'preset'
                            },
                            // Enable user interaction
                            userZoomingEnabled: false,
                            userPanningEnabled: false,
                            boxSelectionEnabled: false,
                            // Enable dragging
                            autoungrabify: false,
                            autounselectify: true
                        });

                        // Add Shape Function:
                        window.addShape = function() {
                            var shape = document.getElementById('shapeInput').value;
                            var label = document.getElementById('labelInput').value;
                            var x = parseFloat(document.getElementById('xInput').value);
                            var y = parseFloat(document.getElementById('yInput').value);

                            var newNode = { 
                                data: { id: 'newShape' + Date.now(), label: label }, 
                                position: { x: x, y: y }
                            };
                            if (shape === 'diamond') {
                                newNode.style = { 'shape': 'diamond' };
                            }

                            cy.add(newNode);
                        }

                        // Optional: Add visible feedback when dragging
                        cy.on('dragfree', 'node', function(evt){
                            var node = evt.target;
                            node.animate({
                                style: { 'border-width': 3, 'border-color': '#ff0000' }
                            }, {
                                duration: 100
                            }).animate({
                                style: { 'border-width': 1, 'border-color': '#346789' }
                            }, {
                                duration: 100
                            });
                        });
                    });
                    """
                ),
                  Script(
            """
            const container = document.getElementById('container');
            const fileInput = document.getElementById('file-upload_');
            const form = document.getElementById('upload-form');;
            
            container.addEventListener('dragover', (event) => {
                event.preventDefault();
            });

            container.addEventListener('drop', (event) => {
                event.preventDefault();

                const files = event.dataTransfer.files;  

                fileInput.files = files; 

                form.dispatchEvent(new Event('submit')); 
            });
            """
        ),
            lang='en'
        )      
    ))

def generate_elements():
    
    with open('diagrams.json', 'r') as f:
        elements = json.load(f)

    cytoscape_elements = []
    for node_id, node_data in elements['nodes'].items():
        cytoscape_elements.append({
            'data': {'id': node_id, 'label': node_data['label']},
            'position': {'x': node_data['x'], 'y': node_data['y']}
        })
        for edge_data in node_data.get('edges', []):
            cytoscape_elements.append({
                'data': {'source': node_id, 'target': edge_data['target']}
            })

    return cytoscape_elements

@rt('/upload')
async def post(request: Request):
    form = await request.form()
    print(f"TEST:")
   
    uploaded_files = form.getlist("file")  # Use getlist to get a list of files

    for uploaded_file in uploaded_files:
        print(f"TEST:")
        
        print(uploaded_file)

        with open(uploaded_file.filename, "wb") as f:
            f.write(uploaded_file.file.read()) 

    # Update the response to display all uploaded filenames
    return Div(
               *[P(f"{uploaded_file.filename}") for uploaded_file in uploaded_files]) 

serve()
