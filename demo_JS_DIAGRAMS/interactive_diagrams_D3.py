

"""
# interactive_diagrams_D3.py
# Using FastHTML and D3.js to create interactive diagrams

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
                Title('D3.js Interactive Flowchart'),
                Script(src='https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js'),
                Style('.flowchart-demo {\r\n            width: 800px;\r\n            height: 600px;\r\n            border: 1px solid #ccc;\r\n        }\r\n        .node {\r\n            cursor: move;\r\n        }\r\n        .link {\r\n            fill: none;\r\n            stroke: #999;\r\n            stroke-width: 1.5px;\r\n        }\r\n        .arrowhead {\r\n            fill: #999;\r\n        }')
            ),
            Body(
                Div(id='flowchart-demo', cls='flowchart-demo'),
                Script('// Define the diagram data\r\n        const nodes = [\r\n            { id: 1, type: "rectangle", label: "Rectangle 1", x: 50, y: 50, width: 150, height: 80 },\r\n            { id: 2, type: "diamond", label: "Diamond", x: 250, y: 200, width: 100, height: 100 },\r\n            { id: 3, type: "rectangle", label: "Rectangle 2", x: 50, y: 350, width: 150, height: 80 }\r\n        ];\r\n\r\n        const links = [\r\n            { source: 1, target: 2 },\r\n            { source: 2, target: 3 }\r\n        ];\r\n\r\n        // Set up the SVG\r\n        const svg = d3.select("#flowchart-demo").append("svg")\r\n            .attr("width", "100%")\r\n            .attr("height", "100%");\r\n\r\n        // Define arrow marker\r\n        svg.append("defs").append("marker")\r\n            .attr("id", "arrowhead")\r\n            .attr("viewBox", "-0 -5 10 10")\r\n            .attr("refX", 20)\r\n            .attr("refY", 0)\r\n            .attr("orient", "auto")\r\n            .attr("markerWidth", 6)\r\n            .attr("markerHeight", 6)\r\n            .attr("xoverflow", "visible")\r\n            .append("svg:path")\r\n            .attr("d", "M 0,-5 L 10 ,0 L 0,5")\r\n            .attr("class", "arrowhead");\r\n\r\n        // Create links\r\n        const link = svg.selectAll(".link")\r\n            .data(links)\r\n            .enter().append("line")\r\n            .attr("class", "link")\r\n            .attr("marker-end", "url(#arrowhead)");\r\n\r\n        // Create nodes\r\n        const node = svg.selectAll(".node")\r\n            .data(nodes)\r\n            .enter().append("g")\r\n            .attr("class", "node")\r\n            .attr("transform", d => `translate(${d.x},${d.y})`)\r\n            .call(d3.drag()\r\n                .on("drag", dragged)\r\n                .on("end", dragended));\r\n\r\n        // Add shapes to nodes\r\n        node.each(function(d) {\r\n            if (d.type === "rectangle") {\r\n                d3.select(this).append("rect")\r\n                    .attr("width", d.width)\r\n                    .attr("height", d.height)\r\n                    .attr("fill", "#f0f0f0")\r\n                    .attr("stroke", "#346789");\r\n            } else if (d.type === "diamond") {\r\n                d3.select(this).append("polygon")\r\n                    .attr("points", `0,${d.height/2} ${d.width/2},0 ${d.width},${d.height/2} ${d.width/2},${d.height}`)\r\n                    .attr("fill", "#f0f0f0")\r\n                    .attr("stroke", "#346789");\r\n            }\r\n        });\r\n\r\n        // Add labels to nodes\r\n        node.append("text")\r\n            .attr("text-anchor", "middle")\r\n            .attr("dominant-baseline", "middle")\r\n            .attr("transform", d => d.type === "diamond" ? "rotate(45)" : null)\r\n            .attr("x", d => d.width / 2)\r\n            .attr("y", d => d.height / 2)\r\n            .text(d => d.label);\r\n\r\n        // Define drag behavior\r\n        function dragged(event, d) {\r\n            d3.select(this).attr("transform", `translate(${d.x = event.x}, ${d.y = event.y})`);\r\n            updateLinks();\r\n        }\r\n\r\n        function dragended(event, d) {\r\n            updateLinks();\r\n        }\r\n\r\n        // Update link positions\r\n        function updateLinks() {\r\n            link\r\n                .attr("x1", d => nodes[d.source - 1].x + nodes[d.source - 1].width / 2)\r\n                .attr("y1", d => nodes[d.source - 1].y + nodes[d.source - 1].height / 2)\r\n                .attr("x2", d => nodes[d.target - 1].x + nodes[d.target - 1].width / 2)\r\n                .attr("y2", d => nodes[d.target - 1].y + nodes[d.target - 1].height / 2);\r\n        }\r\n\r\n        // Initial update of links\r\n        updateLinks();')
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
