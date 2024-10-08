

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
        Div(
            Div(
                Title('Cytoscape.js Interactive Flowchart'),
                Div("Uploaded File:", id="uploaded-file"),
                Form(
                    Input(type='file', id='file-upload_', name='files', style="display: none", 
                          onchange="document.getElementById('submit-upload-btn').click()", accept=".txt, .xlsx, .docx, .json, .pdf, .html"),
                    Button('Select Files', cls="select-files-btn", type='button', onclick="document.getElementById('file-upload_').click()"),
                    Button(type="submit", 
                           id="submit-upload-btn", 
                           style="display: none",
                           ),
                    **{'hx-on:htmx:after-request':"draw();"},
                    id="upload-form",
                    hx_post="/upload",
                    target_id="flowchart-demo",
                    hx_swap="outerHTML",
                    enctype="multipart/form-data"
                ),
                Script(src='https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.23.0/cytoscape.min.js'),
                Style('#flowchart-demo {\r\n            width: 800px;\r\n            height: 600px;\r\n            border: 1px solid #ccc;\r\n        }'),
                
            ),
            Div(id='flowchart-demo')
        )      
    )

def get_diagram(filename):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    dir_out = script_dir + "/uploaded_diagram"
    file_path = dir_out + "/" + filename 

    with open(file_path, 'r') as file:
        data = json.load(file)
        return data


def generate_elements(filename):

    elements = get_diagram(filename)

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
    script_dir = os.path.dirname(os.path.realpath(__file__))
    dir_out = script_dir + "/uploaded_diagram"
    
    form = await request.form()
   
    uploaded_files = form.getlist("files")  # Use getlist to get a list of files

    print(f"uploaded_files: {form}")
    uploaded_file = uploaded_files[0]
    print(f"uploaded file: {uploaded_file}")

    os.makedirs(dir_out, exist_ok=True)

    with open(f"{dir_out}/{uploaded_file.filename}", "wb") as f:
        f.write(uploaded_file.file.read()) 

    diagram = Div(
                Script(
                    """
                    function draw() {
                    //alert("1");
                    //document.addEventListener('DOMContentLoaded', function() {
                        var cy = cytoscape({
                            container: document.getElementById('flowchart-demo'),
                            elements: """ + json.dumps(generate_elements(uploaded_file.filename)) + """,
                            style: [
                                {
                                    selector: 'node',
                                    style: {
                                        'shape': 'rectangle',
                                        'background-color': '#f0f0f0',
                                        'border-color': '#346789',
                                        'border-width': 1,
                                        'label': 'data(label)',
                                        'text-valign': 'center',
                                        'text-halign': 'center',
                                        'width': 80,
                                        'height': 40,
                                        'font-size': 10
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
                                        'width': 1,
                                        'line-color': '#999',
                                        'target-arrow-color': '#999',
                                        'target-arrow-shape': 'triangle',
                                        'curve-style': 'bezier',
                                        'arrow-scale': 0.8
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
                    //});
                    }
                    """
                ),

                id='flowchart-demo')
    
    return diagram, Div(f"Uploaded File: {uploaded_file.filename}", id="uploaded-file", hx_swap_oob='true')

serve()
