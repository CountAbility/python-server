from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.orm import Session
from ultralytics import YOLO
import crud
import models
import schemas
from database import SessionLocal, engine
from fastapi import FastAPI, WebSocket
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

        #output = localize_bytes(data)

        #output = [(object_.name, object_.score) for object_ in output if object_.score > 0.5]

        #output = sorted(output, key=lambda x: x[1], reverse=True)

        #if output is not [[]]:
        #    output = output[0][0]

        model = YOLO("/Users/malcolmkrolick/Documents/GitHub/python-server/best.pt")
        
        # Decode the base64 string
        decoded_bytes = base64.b64decode(data)
        
        # Convert bytes to numpy array
        img = np.frombuffer(decoded_bytes, np.uint8)

        class_names = ["scissors", "knife"]

        results = model(img)

        classes_gen = []
        # coordinates
        for r in results:
            boxes = r.boxes

            for box in boxes:

                confidence = math.ceil((box.conf[0]*100))/100

                class_name = class_names[int(box.cls[0])]

                classes_gen.append((class_name, confidence))

        classes_gen = [x for x in classes_gen if x[1] > 0.5]

        classes_gen = sorted(classes_gen, key=lambda x: x[1], reverse=True)

        print(classes_gen)

        await websocket.send_json(classes_gen)




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