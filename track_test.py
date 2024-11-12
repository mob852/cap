import cv2

# Initialize video capture (0 for the first camera, or a file path for a video)
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
    
    # Capture frame-by-frame
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

    # Display the frame
    cv2.imshow("Object Tracking", frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
