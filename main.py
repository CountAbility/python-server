from fastapi import FastAPI, WebSocket
from tools import localize_bytes
from time import sleep

app = FastAPI()

@app.websocket("/feed")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()

        #print(data)

        data = data.split(",")[1]

        output = localize_bytes(data)

        print(output)






