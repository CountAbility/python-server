import time
from datetime import datetime
from random import randint
from uuid import UUID

from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from ultralytics import YOLO
import crud
import models
import schemas
from alert_manager import AlertManager
from database import SessionLocal, engine
from fastapi import FastAPI, WebSocket

from diffengine import DiffEngine
from tools import localize_bytes
from time import sleep
from ml_tools import img_object_detection
import numpy as np
from PIL import Image
import cv2
import base64
import math

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
initials = ['knife', 'knife']
diff_engine = DiffEngine()
diff_engine.set_initial_items(initials)


@app.websocket("/feed")
async def camera_feed(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            try:
                data = await websocket.receive_json()
                if (datetime.now().timestamp() - data["timestamp"]) > 2:
                    continue

                if not data["image"]:
                    await websocket.send_json({})
                    continue




                # output = localize_bytes(data)

                # output = [(object_.name, object_.score) for object_ in output if object_.score > 0.5]

                # output = sorted(output, key=lambda x: x[1], reverse=True)

                # if output is not [[]]:
                #    output = output[0][0]

                model = YOLO("best.pt")

                # Decode the base64 string
                decoded_bytes = base64.b64decode(data["image"])
                print(data["image"][1:100])

                # Convert bytes to numpy array
                img = cv2.imdecode(np.frombuffer(decoded_bytes, np.uint8), cv2.IMREAD_COLOR)

                class_names = ["scissors", "knife"]
                results = model(img)

                classes_gen = []
                # coordinates
                for r in results:
                    boxes = r.boxes

                    for box in boxes:
                        confidence = math.ceil((box.conf[0] * 100)) / 100

                        class_name = class_names[int(box.cls[0])]

                        classes_gen.append((class_name, confidence))

                classes_gen = [x for x in classes_gen if x[1] > 0.5]

                classes_gen = sorted(classes_gen, key=lambda x: x[1], reverse=True)

                print(classes_gen)

                diff_engine.set_current_items(map(lambda x: x[0], classes_gen))
                diff = diff_engine.compare()
                print(diff)

                crud.delete_alerts(db)

                for k in diff:
                    for i in range(diff[k]):
                        alert = schemas.AlertCreate(
                            surgery_id=UUID(data["surgery"]),
                            message=f"Missing {k}",
                            severity=diff_engine.surgery_status,
                            time_started=datetime.now()
                        )

                        crud.create_alert(db, alert)

                await alert_manager.broadcast_alerts(db, UUID(data["surgery"]))

                print(datetime.now().timestamp())

                await websocket.send_json(classes_gen)
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
@app.get("/initialitems")
def get_initial_items():
    return initials

@app.get("/updatestatus/{status}")
def update_status(status):
    diff_engine.surgery_status = status

