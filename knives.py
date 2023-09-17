
import cv2 as cv
import numpy as np
import math
from PIL import Image
from ultralytics import YOLO
from collections import defaultdict
import time
from matplotlib import pyplot as plt


# WEBCAM STUFF                #
# cap = cv.VideoCapture(0)    #
# cap.set(3, 640)             #
# cap.set(4, 480)             #






model = YOLO("C:/Users/malco/Desktop/CountAbility/SurgicalModel/runs/detect/train/weights/best.pt")

img = "SurgicalModel/knives.jpg"
img = np.array(Image.open(img))




class_names = ["scissors", "knife"]

results = model(img)

# coordinates
for r in results:
    boxes = r.boxes

    for box in boxes:

        class_name = class_names[int(box.cls[0])]

        print(class_name)

#         # bounding box
#         x1, y1, x2, y2 = box.xyxy[0]
#         x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

#         # confidence
#         confidence = math.ceil((box.conf[0]*100))/100
#         print("Confidence --->",confidence)

#         # if confidence < 0.5:
#         #     continue

#         # put box in cam
#         cv.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

#         # class name
#         cls = int(box.cls[0])
#         print("Class name -->", class_names[cls])

#         # object details
#         org = [x1, y1]
#         font = cv.FONT_HERSHEY_SIMPLEX
#         fontScale = 1
#         color = (255, 0, 0)
#         thickness = 2

#         cv.putText(img, class_names[cls], org, font, fontScale, color, thickness)
#         print("Object details -->", class_names[cls], org, font, fontScale, color, thickness)

# plt.imshow(img)
# plt.show()


































# cv.imshow('img', img)

# time.sleep(10)

# cv.destroyAllWindows()


# while True:
#     success, img = cap.read()
#     results = model(img, stream=True)

#     # coordinates
#     for r in results:
#         boxes = r.boxes

#         for box in boxes:
#             # bounding box
#             x1, y1, x2, y2 = box.xyxy[0]
#             x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

#             # confidence
#             confidence = math.ceil((box.conf[0]*100))/100
#             print("Confidence --->",confidence)

#             if confidence > 0.6:
            
#                 # put box in cam
#                 cv.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

#                 # class name
#                 cls = int(box.cls[0])
#                 print("Class name -->", class_names[cls])

#                 # object details
#                 org = [x1, y1]
#                 font = cv.FONT_HERSHEY_SIMPLEX
#                 fontScale = 1
#                 color = (255, 0, 0)
#                 thickness = 2

#                 cv.putText(img, class_names[cls], org, font, fontScale, color, thickness)

#     cv.imshow('Webcam', img)
#     if cv.waitKey(1) == ord('q'):
#         break

# cap.release()
# cv.destroyAllWindows()