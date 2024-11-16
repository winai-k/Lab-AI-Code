import cv2
import subprocess
import yt_dlp

# The YouTube live stream URL
youtube_url = "https://www.youtube.com/watch?v=7EEy1OEmGjc" #"https://www.youtube.com/watch?v=yJYGeP1vEhs" # Moo Deng Live

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

# Display the live stream
while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to grab frame.")
        break
    
    cv2.imshow('YouTube Live Feed', frame)
    
    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()