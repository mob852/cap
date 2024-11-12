import cv2

# Create a VideoCapture object to access the USB camera
cap = cv2.VideoCapture(0)  # 0 is usually the default camera

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

# Capture a single frame from the camera
ret, frame = cap.read()

if not ret:
    print("Error: Could not read frame.")
else:
    # Save the captured frame as an image file
    cv2.imwrite('photo.jpg', frame)
    print("Photo captured and saved as 'photo.jpg'")

# Release the VideoCapture object and close any OpenCV windows
cap.release()
# cv2.destroyAllWindows()
