import os
import cv2
import subprocess
import yt_dlp

# The YouTube live stream URL
youtube_url = "https://www.youtube.com/watch?v=7EEy1OEmGjc" #"https://www.youtube.com/watch?v=yJYGeP1vEhs" # Moo Deng Live
# youtube_url = "https://www.youtube.com/watch?v=gFRtAAmiFbE&list=PLxtg5zfgORZr8KB1VglBvI6czMJpPL-rx" # Kabukicho Live Channel II

# + Create directory to save frames
save_dir = "frames"
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

# Display the live stream
while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame,(1200,800))
    
    if not ret:
        print("Failed to grab frame.")
        break
    
    # + Save each frame to the folder
    frame_filename = os.path.join(save_dir, f"frame_{frame_count}.jpg")
    cv2.imwrite(frame_filename, frame)
    frame_count += 1

    cv2.imshow('YouTube Live Feed', frame)
    
    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()