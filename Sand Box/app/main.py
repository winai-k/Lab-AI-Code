from fastapi import FastAPI, File, UploadFile, Path, Query
from ultralytics import YOLO
import cv2
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt

app = FastAPI()
model = YOLO("weights/yolov8n.pt")

@app.get("/api/v1/class-info")
async def model_class_info():
    return model.names

@app.post("/api/v1/detect/{class_id}")
async def detection(image: UploadFile, 
                    conf: float = Query(0.8, title="confidence threshold", gt=0), 
                    device: str = Query("cpu", title="device for inference (cpu, 0, 1)"),
                    class_id: int = Path(..., title="class id of object")):
    """
    ## bbox format = x1, y1, x2, y2
    """
    resp = {"status": 200, "object": []}
    img = image.file.read()
    np_array = np.frombuffer(img, np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    results = model.predict(img, conf=conf, show_labels=True, device=device, vid_stride=3, verbose=False)
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy.squeeze().tolist()
            confidence = round(box.conf.squeeze().tolist(), 2)
            obj_class = int(box.cls[0])
            label = model.names[obj_class]
            if obj_class != class_id:
                continue
            resp["object"].append({"bbox": {"x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2)}, 
                                   "label": label, "conf": confidence})
    return resp