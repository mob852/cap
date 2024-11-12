import cv2
from datetime import datetime  # Import datetime module

# Create a VideoCapture object to access the USB camera
cap = cv2.VideoCapture(0)  # 0 is usually the default camera

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

# Define the codec and create a VideoWriter object to save the video
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can use other codecs like 'MJPG', 'X264', etc.
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

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
    cv2.putText(frame, timestamp_text, (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    # Write the frame to the video file
    out.write(frame)

    # Display the captured frame in a window named 'Camera'
    cv2.imshow('Camera', frame)

    # Check if the user pressed the 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture and VideoWriter objects, and close any OpenCV windows
cap.release()
out.release()
cv2.destroyAllWindows()

