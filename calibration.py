import cv2
import numpy as np
import time

# Define the chessboard dimensions and square size
chessboard_size = (5, 8)  # Number of internal corners (cross points) in your chessboard
square_size = 29.0  # Size of a square in millimeters (adjust according to your chessboard)

# Prepare object points, e.g. (0,0,0), (29,0,0), (58,0,0) ... (145,203,0)
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size

# Arrays to store object points and image points from all the images
objpoints = []  # 3D points in real-world space
imgpoints = []  # 2D points in image plane

# Create a VideoCapture object to access the USB camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

capture_count = 0
max_images = 15  # Set the maximum number of images to capture

while capture_count < max_images:
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Could not read frame.")
        break
    
    # Convert to grayscale for corner detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Find the chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                                    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        imgpoints.append(corners2)

        # Draw and display the corners
        frame_with_corners = cv2.drawChessboardCorners(frame, chessboard_size, corners2, ret)
        cv2.imshow('Chessboard', frame_with_corners)

        # Save the captured frame
        filename = f'chessboard_image_{capture_count}.jpg'
        cv2.imwrite(filename, frame_with_corners)
        print(f"Captured and saved {filename}")

        capture_count += 1

    # Wait for 3 seconds before capturing the next image
    time.sleep(3)

    # Display the current frame
    cv2.imshow('Camera', frame)

    # Check if the user pressed the 'q' key to exit early
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Perform camera calibration
ret, camera_matrix, distortion_coefficients, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Save the calibration results
np.savez('calibration_data.npz', camera_matrix=camera_matrix, dist_coeff=distortion_coefficients, rvecs=rvecs, tvecs=tvecs)

print("Calibration complete.")
print("Camera matrix:\n", camera_matrix)
print("Distortion coefficients:\n", distortion_coefficients)

