import cv2
import base64
from ml_tools import img_object_detection, localize_bytes

# Read the image using OpenCV
image = cv2.imread("./images/Lork.jpg")

#show the image
cv2.imshow("image", image)

# Encode the image as JPEG (you can also use PNG or other formats)
retval, encoded_image = cv2.imencode(".jpg", image)

# Convert the encoded image bytes to base64
encoded_string = base64.b64encode(encoded_image).decode("uthf-8")

test = localize_bytes(encoded_string)
print(test)