from datetime import datetime
from random import randint
from uuid import UUID

from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

import crud
import models
import schemas
from alert_manager import AlertManager
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


alert_manager = AlertManager()


@app.websocket("/feed")
async def camera_feed(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            try:
                data = await websocket.receive_json()

                if not data["image"]:
                    await websocket.send_json({})
                    continue

                alert = schemas.AlertCreate(
                    surgery_id=UUID(data["surgery"]),
                    message="Alert!!",
                    severity=randint(1, 4),
                    time_started=datetime.now()
                )

                crud.create_alert(db, alert)
                await alert_manager.broadcast_alerts(db, UUID(data["surgery"]))

                output = img_object_detection(data["image"], save_boxes=True)

                await websocket.send_json(output)
            except WebSocketDisconnect:
                pass
    except WebSocketDisconnect:
        pass


@app.websocket("/alerts")
async def alert_feed(websocket: WebSocket):
    await alert_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
    except WebSocketDisconnect:
        alert_manager.disconnect(websocket)


@app.post("/createsurgery", response_model=schemas.SurgicalRecord)
def create_surgery(surgery: schemas.SurgicalRecordCreate, db: Session = Depends(get_db)):
    print(surgery)
    return crud.create_surgery(db, surgery)


@app.get("/surgeries")
def get_surgeries(db: Session = Depends(get_db)):
    return crud.get_surgeries(db)
