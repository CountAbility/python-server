from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import SessionLocal, engine
from fastapi import FastAPI, WebSocket
from tools import localize_bytes
from time import sleep
from ml_tools import img_object_detection

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.websocket("/feed")
async def camera_feed(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        if str(data) == 'null' or not data:
            await websocket.send_json({})
            continue

        #print(data)
        print(data[0:100])

        data = data.split(",")[1]

        output = img_object_detection(data, save_boxes=True)

        await websocket.send_json(output)


@app.websocket("/alerts")
async def alert_feed(websocket: WebSocket):
    await websocket.accept()


@app.post("/createsurgery", response_model=schemas.SurgicalRecord)
def create_surgery(surgery: schemas.SurgicalRecordCreate, db: Session = Depends(get_db)):
    print(surgery)
    return crud.create_surgery(db, surgery)


@app.get("/surgeries")
def get_surgeries(db: Session = Depends(get_db)):
    return crud.get_surgeries(db)