import io
import cv2
import numpy as np
from scipy.ndimage import label
from google.cloud import vision

# Load the image and preprocess
image_path = "images/Lork.jpg"
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Blur the image
kernel_size = (5, 5)  # you can adjust the kernel size as needed
image = cv2.GaussianBlur(image, kernel_size, 0)

image = cv2.bitwise_not(image)

if image is not None:
    threshold_value = 20
    _, mask = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
    cv2.imwrite("mask.png", mask)

else:
    print("Failed to load the image.")



def localize_bytes(bytes):
    """Localize objects in the local image.

    Args:
    path: The path to the local file.
    """

    client = vision.ImageAnnotatorClient()

    content = bytes
    image = vision.Image(content=content)

    objects = client.object_localization(image=image).localized_object_annotations

    #print(f"Number of objects found: {len(objects)}")
    #for object_ in objects:
        #print(f"\n{object_.name} (confidence: {object_.score})")
        #print("Normalized bounding polygon vertices: ")
    #    for vertex in object_.bounding_poly.normalized_vertices:
            #print(f" - ({vertex.x}, {vertex.y})")

    return objects





def extract_bboxes(mask):
    """Compute bounding boxes from masks.
    mask: [height, width, num_instances]. Mask pixels are either 1 or 0.
    Returns: bbox array [num_instances, (y1, x1, y2, x2)].
    """

    boxes = np.zeros([mask.shape[-1], 4], dtype=np.int32)
    for i in range(mask.shape[-1]):
        m = mask[:, :, i]
        horizontal_indicies = np.where(np.any(m, axis=0))[0]
        vertical_indicies = np.where(np.any(m, axis=1))[0]
        if horizontal_indicies.shape[0]:
            x1, x2 = horizontal_indicies[[0, -1]]
            y1, y2 = vertical_indicies[[0, -1]]
            x2 += 1
            y2 += 1
        else:
            x1, x2, y1, y2 = 0, 0, 0, 0
        boxes[i] = np.array([y1, x1, y2, x2])
    return boxes.astype(np.int32)


def parse_output(output):
    lines = output.strip().split('\n')

    num_objects = int(lines[0].split(":")[1].strip())

    objects = []

    i = 1
    while i < len(lines):
        obj = {}

        # Extract object name and confidence
        name_confidence = lines[i].split(" (confidence: ")
        obj['name'] = name_confidence[0].strip()
        obj['confidence'] = float(name_confidence[1].rstrip(')'))

        # Extract bounding polygon vertices
        vertices = []
        i += 2  # Move to first vertex
        while i < len(lines) and lines[i].startswith('-'):
            coords = lines[i].split('(')[1].rstrip(')').split(',')
            x = float(coords[0].strip())
            y = float(coords[1].strip())
            vertices.append((x, y))
            i += 1

        obj['vertices'] = vertices

        objects.append(obj)

        # Skip one line for the next object
        i += 1

    return objects





# Read mask.png
mask = cv2.imread("mask.png", cv2.IMREAD_GRAYSCALE)

# Convert the 2D mask into 3D mask (height, width, num_instances)
# Here, we're treating each unique value (excluding 0) as an instance.
labeled_mask, num_features = label(mask)
mask_3d = np.stack([labeled_mask == i for i in range(1, num_features + 1)], axis=-1)

# Extract bounding boxes
boxes = extract_bboxes(mask_3d)

# Set a minimum percentage threshold for bounding box area
min_percentage = 10.0  # 1% of the total image area
min_area = (image.shape[0] * image.shape[1] * min_percentage) / 100

# Filter bounding boxes based on the minimum area
filtered_boxes = []
for box in boxes:
    y1, x1, y2, x2 = box
    box_area = (y2 - y1) * (x2 - x1)
    if box_area >= min_area:
        filtered_boxes.append(box)
boxes = np.array(filtered_boxes)


# Display the bounding boxes on the original image
image_with_bboxes = cv2.imread(image_path)  # Load the original image in color
for box in boxes:
    y1, x1, y2, x2 = box
    cv2.rectangle(image_with_bboxes, (x1, y1), (x2, y2), (0, 255, 0), 2)  # The color is set to green and line thickness is 2

# Save the image with bounding boxes
cv2.imwrite("image_with_bboxes.png", image_with_bboxes)

# Load the original colored image
colored_image = cv2.imread(image_path)


objects_list = []
segment_bytes_list = []
# Extract colored segments based on bounding boxes and save them
for idx, box in enumerate(boxes):
    y1, x1, y2, x2 = box
    colored_segment = colored_image[y1:y2, x1:x2]

    # Image saving 
    #segment_filename = f"colored_segment_{idx}.png"
    #cv2.imwrite(segment_filename, colored_segment)

    is_success, buffer = cv2.imencode(".png", colored_segment)
    if is_success:
        io_buf = io.BytesIO(buffer)
        segment_bytes = io_buf.getvalue()
        segment_bytes_list.append(segment_bytes)
    else:
        print(f"Failed to convert segment {idx} to bytes")
    
    

    objects = localize_bytes(segment_bytes)
    
    filtered_objects = [(object_.name, object_.score) for object_ in objects if object_.score > 0.5]
    #print(filtered_objects)

    objects_list.append(filtered_objects)

#sort inner object list by object score
objects_list = [sorted(objects, key=lambda x: x[1], reverse=True) for objects in objects_list]

#print(objects_list)

# filter objects to remove second object in each segment
objects_list = [objects[0] for objects in objects_list]
print(objects_list)

    




# Send the colored segments to the model for inference





