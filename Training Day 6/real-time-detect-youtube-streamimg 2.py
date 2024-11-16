from ultralytics import YOLO
import cv2
import yt_dlp

# The YouTube live stream URL
youtube_url = "https://www.youtube.com/watch?v=7EEy1OEmGjc" # Moo Deng Live

# Load the YOLOv8 model
model = YOLO('../Training Day 6/runs/yolov8_experiment/weights/best.pt')

# Function to get the direct stream URL
def get_youtube_stream_url(youtube_url):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
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
    0: 'Moo Deng',  # ใส่ชื่อ class ตามที่คุณเทรนโมเดลไว้
    1: 'Mom',
    # เพิ่ม class อื่นๆ ตามที่คุณมี
}

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

# กำหนดการบันทึกวิดีโอ
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter('output.mp4', 
                     cv2.VideoWriter_fourcc(*'mp4v'),
                     30, # FPS
                     (frame_width, frame_height))

frame_count = 0
max_frames = 300  # จำนวนเฟรมที่ต้องการบันทึก (ประมาณ 10 วินาที ที่ 30 FPS)

while frame_count < max_frames:
    ret, frame = cap.read()
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

    # บันทึกเฟรม
    out.write(frame)
    frame_count += 1
    print(f"Processing frame {frame_count}/{max_frames}")

cap.release()
out.release()
print("Video processing completed. Output saved as 'output.mp4'")