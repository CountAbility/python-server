from fastapi import FastAPI, WebSocket


app = FastAPI()

@app.websocket("/feed")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()