import cv2
import time
import subprocess
from datetime import datetime  # Import datetime module

def git_commit_and_push(filename):
    try:
        # Add file to staging
        subprocess.run(['git', 'add', filename], check=True)
        
        # Commit changes
        commit_message = f"Add image {filename}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push changes
        subprocess.run(['git', 'push'], check=True)
        print(f"Committed and pushed {filename} to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during Git operations: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Create a VideoCapture object to access the USB camera
cap = cv2.VideoCapture(0)  # 0 is usually the default camera

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

try:
    while True:
        # Capture a single frame from the camera
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
        else:
            # Get current time and format it
            now = datetime.now()
            timestamp_str = now.strftime("%Y%m%d_%H%M%S")
            filename = f'photo_{timestamp_str}.jpg'
            
            # Save the captured frame as an image file
            cv2.imwrite(filename, frame)
            print(f"Photo captured and saved as '{filename}'")

            # Commit and push the image to GitHub
            git_commit_and_push(filename)

        # Wait for 10 seconds
        time.sleep(1800)

except KeyboardInterrupt:
    print("Process interrupted by the user.")

finally:
    # Release the VideoCapture object
    cap.release()
