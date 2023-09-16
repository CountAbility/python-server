from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import SessionLocal, engine
from fastapi import FastAPI, WebSocket
from tools import localize_bytes
from time import sleep

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

        #print(data)

        data = data.split(",")[1]

        output = localize_bytes(data)

        print(output)
        await websocket.send_json({})


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