

"""
# interactive_diagrams_D3.py
# Using FastHTML and D3.js to create interactive diagrams

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
                Title('D3.js Interactive Flowchart'),
                Div("Uploaded File:", id="uploaded-file"),
                Script(src='https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js'),
                Style('#flowchart-demo {\r\n            width: 800px;\r\n            height: 600px;\r\n            border: 1px solid #ccc;\r\n        }\r\n        .node {\r\n            cursor: move;\r\n        }\r\n        .link {\r\n            fill: none;\r\n            stroke: #999;\r\n            stroke-width: 1.5px;\r\n        }\r\n        .arrowhead {\r\n            fill: #999;\r\n        }')
            ),
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
            Div(id='flowchart-demo')
        )    
    )

def get_nodes(diagram_):

    flowchart_data = diagram_
    print(diagram_)
    nodes = [{k: v for k, v in element.items() if k != 'links'} for element in flowchart_data['elements']]

    return nodes

def get_links(diagram_):

    flowchart_data = diagram_
    links = [{"source": link["source"], "target": element["id"]} 
             for element in flowchart_data['elements'] 
             for link in element["links"]]
    
    return links

@rt('/upload')
async def post(request: Request):
    
    global diagram_

    script_dir = os.path.dirname(os.path.realpath(__file__))
    dir_out = script_dir + "/uploaded_diagram2"
    
    form = await request.form()
   
    uploaded_files = form.getlist("files")  # Use getlist to get a list of files

    print(f"uploaded_files: {form}")
    uploaded_file = uploaded_files[0]
    print(f"uploaded file: {uploaded_file}")

    os.makedirs(dir_out, exist_ok=True)

    with open(f"{dir_out}/{uploaded_file.filename}", "wb") as f:
        f.write(uploaded_file.file.read()) 

    with open(f"{dir_out}/{uploaded_file.filename}", 'r') as file:
        data = json.load(file)
        diagram_ = data

    # Update the response to display all uploaded filenames
    return Div(
                Script(
                    """
                    // Define the diagram data
                    const nodes = """ + json.dumps(get_nodes(diagram_)) + """;

                    const links = """ + json.dumps(get_links(diagram_)) + """;

                    // Set up the SVG
                    const svg = d3.select("#flowchart-demo").append("svg")
                    .attr("width", "100%")
                    .attr("height", "100%");

                    // Define arrow marker
                    svg.append("defs").append("marker")
                    .attr("id", "arrowhead")
                    .attr("viewBox", "-0 -5 10 10")
                    .attr("refX", 20)
                    .attr("refY", 0)
                    .attr("orient", "auto")
                    .attr("markerWidth", 6)
                    .attr("markerHeight", 6)
                    .attr("xoverflow", "visible")
                    .append("svg:path")
                    .attr("d", "M 0,-5 L 10 ,0 L 0,5")
                    .attr("class", "arrowhead");

                    // Create links
                    const link = svg.selectAll(".link")
                    .data(links)
                    .enter().append("line")
                    .attr("class", "link")
                    .attr("marker-end", "url(#arrowhead)");

                    // Create nodes
                    const node = svg.selectAll(".node")
                    .data(nodes)
                    .enter().append("g")
                    .attr("class", "node")
                    .attr("transform", d => `translate(${d.x},${d.y})`)
                    .call(d3.drag()
                        .on("drag", dragged)
                        .on("end", dragended));

                    // Add shapes to nodes
                    node.each(function(d) {
                    if (d.type === "rectangle") {
                        d3.select(this).append("rect")
                        .attr("width", d.width)
                        .attr("height", d.height)
                        .attr("fill", "#f0f0f0")
                        .attr("stroke", "#346789");
                    } else if (d.type === "diamond") {
                        d3.select(this).append("polygon")
                        .attr("points", `0,${d.height / 2} ${d.width / 2},0 ${d.width},${d.height / 2} ${d.width / 2},${d.height}`)
                        .attr("fill", "#f0f0f0")
                        .attr("stroke", "#346789");
                    }
                    });

                    // Add labels to nodes
                    node.append("text")
                    .attr("text-anchor", "middle")
                    .attr("dominant-baseline", "middle")
                    .attr("transform", d => (d.type === "diamond" ? "rotate(45)" : null))
                    .attr("x", d => d.width / 2)
                    .attr("y", d => d.height / 2)
                    .text(d => d.label);

                    // Define drag behavior
                    function dragged(event, d) {
                    d3.select(this).attr("transform", `translate(${d.x = event.x}, ${d.y = event.y})`);
                    updateLinks();
                    }

                    function dragended(event, d) {
                    updateLinks();
                    }

                    // Update link positions
                    function updateLinks() {
                    link
                        .attr("x1", d => nodes[d.source - 1].x + nodes[d.source - 1].width / 2)
                        .attr("y1", d => nodes[d.source - 1].y + nodes[d.source - 1].height / 2)
                        .attr("x2", d => nodes[d.target - 1].x + nodes[d.target - 1].width / 2)
                        .attr("y2", d => nodes[d.target - 1].y + nodes[d.target - 1].height / 2);
                    }

                    // Initial update of links
                    updateLinks();
                    """
                ),
            id='flowchart-demo'), Div(f"Uploaded File: {uploaded_file.filename}", id="uploaded-file", hx_swap_oob='true')

serve()
