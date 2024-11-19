from ultralytics import YOLO
import cv2
import yt_dlp

# The YouTube live stream URL
youtube_url = "https://youtu.be/lsxYH2XQQCg?list=PLxtg5zfgORZr8KB1VglBvI6czMJpPL-rx" # 淡路島モンキーセンター Live Channel

# Load the YOLOv8 model (adjust the path to your trained model)
model = YOLO(r'C:\Users\winai\All Data\My AI Data\Training Day 6\Data\monkey-in-a-zoo\runs\yolov8_experiment\weights\best.pt')  # Replace 'best.pt' with the path to your trained model

# Function to get the direct stream URL
def get_youtube_stream_url(youtube_url):
    ydl_opts = {
        'format': 'best',  # Best format available
        'noplaylist': True, # Do not process playlists
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        stream_url = info['url']
        return stream_url

# Get the live stream URL
stream_url = get_youtube_stream_url(youtube_url)

# Open the stream using OpenCV
cap = cv2.VideoCapture(stream_url)

# เพิ่ม dictionary สำหรับแมป class number เป็น class name
class_names = {
    0: 'dear',  # ใส่ชื่อ class ตามที่คุณเทรนโมเดลไว้
    1: 'monkey',
    2: 'person',
    # เพิ่ม class อื่นๆ ตามที่คุณมี
}

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame,(1200,800))

    if not ret:
        print("Failed to grab frame.")
        break

    # Run inference
    results = model(frame)

    # Display results
    for result in results:
        for box in result.boxes:
            coords = box.xyxy[0].tolist()  # แปลง tensor เป็น list
            x1, y1, x2, y2 = map(int, coords)  # แปลงเป็น integer
            
            # แสดงชื่อคลาส
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            # แสดง class name แทน class number
            class_name = class_names.get(cls, f'Unknown-{cls}')  # ถ้าไม่พบ class จะแสดง Unknown-{number}
            label = f'{class_name}: {conf:.2f}'

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow('YOLOv8 Inference', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
