import socket
import pickle
import cv2
from datetime import datetime  # Import datetime module
# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 262144)  # 256 KB receive buffer
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)  # 256 KB send buffer
sock.connect(('192.168.1.67', 12346))  # Connect to the server

# Capture video from webcam
cap = cv2.VideoCapture(0)
# Set the desired resolution (e.g., 1280x720)
# width = 2590
# height = 1944
width = 1920
height = 1080
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # # Resize the frame to reduce resolution (optional)
    # frame = cv2.resize(frame, (1920, 1080))  # Adjust resolution as needed

    # Compress the frame to JPEG format
    ret, frame_jpeg = cv2.imencode('.jpg', frame)
    if not ret:
        continue

    # Serialize the frame (compressed)
    frame_data = pickle.dumps(frame_jpeg)

    #time
    timestamp=datetime.now()
    time_data=pickle.dumps(timestamp)
    # Send the length of the frame data first
    time_len=len(time_data)
    sock.sendall(time_len.to_bytes(4,byteorder='big'))
    sock.sendall(time_data)


    frame_len = len(frame_data)
    sock.sendall(frame_len.to_bytes(4, byteorder='big'))  # Send length as 4 bytes

    # Send the frame data
    sock.sendall(frame_data)

    # Display the frame on the sender side (optional)
    # cv2.imshow('Sending Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
sock.close()
cv2.destroyAllWindows()