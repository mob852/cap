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

# Read one frame to determine the new dimensions after undistortion
ret, frame = cap.read()
if not ret:
    print("Error: Could not read initial frame.")
    cap.release()
    exit()

# Get the original frame dimensions
h, w = frame.shape[:2]

# Compute the optimal camera matrix and ROI for cropping
new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coefficients, (w, h), 1, (w, h))

# Compute the undistorted frame once to determine the dimensions
undistorted_frame = cv2.undistort(frame, camera_matrix, distortion_coefficients, None, new_camera_matrix)

# Crop the undistorted frame based on the ROI
x, y, w, h = roi
undistorted_frame = undistorted_frame[y:y+h, x:x+w]

# Get the corrected frame dimensions
corrected_width = undistorted_frame.shape[1]
corrected_height = undistorted_frame.shape[0]

# Define the codec and create a VideoWriter object with the corrected dimensions
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for AVI files
out = cv2.VideoWriter('undistorted_output.avi', fourcc, 20.0, (corrected_width, corrected_height))

# Start capturing and saving video frames
while True:
    # Capture a frame from the camera
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        break

    # Undistort the frame
    undistorted_frame = cv2.undistort(frame, camera_matrix, distortion_coefficients, None, new_camera_matrix)

    # Crop the undistorted frame
    undistorted_frame = undistorted_frame[y:y+h, x:x+w]

    # # Display the undistorted frame (optional)
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
