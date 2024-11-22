import cv2
from datetime import datetime  # Import datetime module

# Create a VideoCapture object to access the USB camera
cap = cv2.VideoCapture(0)  # 0 is usually the default camera

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

# Set the desired resolution (e.g., 1280x720)
width = 2590
height = 1944
# width = 1920
# height = 1080
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# Define the codec and create a VideoWriter object to save the video
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can use other codecs like 'MJPG', 'X264', etc.
out = cv2.VideoWriter('output_camera2.avi', fourcc, 5.0, (int(cap.get(3)), int(cap.get(4))))

# 创建一个窗口
cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)  # 设置为可调整大小
# 设置窗口大小（例如 640x480）
cv2.resizeWindow("Camera", 640, 480)
while True:
    # Capture a frame from the camera
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    #time
    timestamp=datetime.now()

    # Display the received frame along with the timestamp on the original (distorted) frame
    font = cv2.FONT_HERSHEY_SIMPLEX
    timestamp_text = f"Time: {timestamp}"    
    cv2.putText(frame, timestamp_text, (10, 30), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
    # # Write the frame to the video file
    out.write(frame)

    # # # Display the captured frame in a window named 'Camera'
    # cv2.imshow('Camera', frame)

    # Check if the user pressed the 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture and VideoWriter objects, and close any OpenCV windows
cap.release()
out.release()
cv2.destroyAllWindows()

