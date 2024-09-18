from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>File Upload with Progress</title>
    </head>
    <body>
        <h1>File Upload</h1>
        <input type="file" id="fileInput">
        <button onclick="uploadFile()">Upload</button>
        <progress id="progressBar" value="0" max="100"></progress>

        <script>
            const ws = new WebSocket("ws://localhost:8000/ws"); // Adjust port if needed

            ws.onopen = () => {
                console.log("WebSocket connection established");
            };

            ws.onmessage = (event) => {
                const message = event.data;
                if (message.startsWith("progress:")) {
                    const progress = parseFloat(message.split(":")[1]);
                    document.getElementById("progressBar").value = progress;
                }
            };

            async function uploadFile() {
                const fileInput = document.getElementById("fileInput");
                const file = fileInput.files[0];

                if (file) {
                    const chunkSize = 1024 * 1024; // 1MB chunks
                    let offset = 0;

                    while (offset < file.size) {
                        const chunk = file.slice(offset, offset + chunkSize);
                        offset += chunkSize;

                        const reader = new FileReader();
                        reader.onload = (event) => {
                            const arrayBuffer = event.target.result;
                            ws.send(arrayBuffer);
                        };
                        reader.readAsArrayBuffer(chunk);

                        await new Promise(resolve => setTimeout(resolve, 100)); // Adjust delay if needed
                    }
                }
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        total_size = 0
        received_size = 0

        while True:
            data = await websocket.receive_bytes()

            # Process the received data (e.g., save chunk, analyze, etc.)
            # ... 

            received_size += len(data)

            if total_size == 0:  # First chunk, get total size
                total_size = int(websocket.headers.get("Content-Length", 0))

            progress = (received_size / total_size) * 100 if total_size > 0 else 0
            await websocket.send_text(f"progress:{progress}")

    except WebSocketDisconnect:
        print("WebSocket disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Adjust host and port if needed