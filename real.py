import cv2
import numpy as np

# Load the camera matrix and distortion coefficients (replace with your actual calibration data)
camera_matrix = np.array([[331.35296622, 0, 340.02365206],
                          [0, 331.26558961, 232.88406139],
                          [0, 0, 1]])
distortion_coefficients = np.array([-0.31095868, 0.10632107, -0.00261454, -0.00190512, -0.01574951])

# Create a VideoCapture object to access the USB camera
cap = cv2.VideoCapture(0)  # 0 is usually the default camera

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

# Get the original frame width and height
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create a VideoWriter object to save the video
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can use other codecs like 'MJPG', 'X264', etc.
out = cv2.VideoWriter('undistorted_output.avi', fourcc, 20.0, (frame_width, frame_height))

while True:
    # Capture a frame from the camera
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    # Get the dimensions of the frame
    h, w = frame.shape[:2]

    # Compute the optimal camera matrix and undistort the image
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coefficients, (w, h), 1, (w, h))
    undistorted_frame = cv2.undistort(frame, camera_matrix, distortion_coefficients, None, new_camera_matrix)

    # Optionally crop the image if needed based on the ROI
    x, y, w, h = roi
    undistorted_frame = undistorted_frame[y:y+h, x:x+w]

    # Display the undistorted frame
    # cv2.imshow('Undistorted Camera', undistorted_frame)

    # Write the undistorted frame to the video file
    out.write(undistorted_frame)

    # Check if the user pressed the 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture and VideoWriter objects, and close any OpenCV windows
cap.release()
out.release()
cv2.destroyAllWindows()
