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

# Wait until the first frame is available
ret, frame = cap.read()
if not ret:
    print("Error: Could not read the video feed.")
    cap.release()
    exit()

# Select the object to track by drawing a bounding box on the first frame
bbox = cv2.selectROI("Select Object to Track", frame, False)
cv2.destroyWindow("Select Object to Track")

# Initialize the CSRT tracker (good for accuracy but slightly slower)
tracker = cv2.TrackerCSRT_create()
tracker.init(frame, bbox)

# List to store the object's path
path_points = []




while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Update tracker with the current frame
    success, box = tracker.update(frame)

    if success:
        # Unpack the box coordinates
        x, y, w, h = [int(v) for v in box]
        
        # Calculate the center of the object
        center_x, center_y = x + w // 2, y + h // 2
        path_points.append((center_x, center_y))

        # Draw the bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Draw the path (track)
        for i in range(1, len(path_points)):
            cv2.line(frame, path_points[i - 1], path_points[i], (255, 0, 0), 2)

        # Display the center coordinates of the object
        cv2.putText(frame, f"Location: ({center_x}, {center_y})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    else:
        # If tracking fails, display a message
        cv2.putText(frame, "Tracking failed", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)


    # Resize the frame to reduce resolution (optional)
    frame = cv2.resize(frame, (640, 480))  # Adjust resolution as needed

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