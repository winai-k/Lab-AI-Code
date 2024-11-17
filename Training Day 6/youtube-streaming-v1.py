import os
import cv2
import subprocess
import yt_dlp
import time

# The YouTube live stream URL
# youtube_url = "https://www.youtube.com/watch?v=7EEy1OEmGjc" #"https://www.youtube.com/watch?v=yJYGeP1vEhs" # Moo Deng Live
youtube_url = "https://www.youtube.com/watch?v=gFRtAAmiFbE&list=PLxtg5zfgORZr8KB1VglBvI6czMJpPL-rx" # Kabukicho Live Channel II
# youtube_url = "https://youtu.be/lsxYH2XQQCg?list=PLxtg5zfgORZr8KB1VglBvI6czMJpPL-rx" # 淡路島モンキーセンター Live Channel

# + Create directory to save frames
save_dir = r"C:\Users\winai\All Data\My AI Data\Training Day 6\Data\Train image"
os.makedirs(save_dir, exist_ok=True)

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

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

frame_count = 0
last_save_time = time.time()  # เพิ่มตัวแปรเก็บเวลาบันทึกล่าสุด
save_interval = 20  # ระยะเวลาในการบันทึกภาพ (วินาที)

# Display the live stream
while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame,(1200,800))
    
    if not ret:
        print("Failed to grab frame.")
        break
    
    current_time = time.time()
    if current_time - last_save_time >= save_interval:
        frame_filename = os.path.join(save_dir, f"f_{frame_count}.jpg")
        cv2.imwrite(frame_filename, frame)
        print(f"บันทึกภาพที่ {frame_count} เวลา: {time.strftime('%H:%M:%S')}")
        frame_count += 1
        last_save_time = current_time  # อัพเดทเวลาบันทึกล่าสุด

    cv2.imshow('YouTube Live Feed', frame)
    
    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()