import cv2
import time
from config import COMMAND_DELAY, LEFT_THRESHOLD, RIGHT_THRESHOLD
from vision import init_vision, detect_objects
from serial_comm import init_serial, send_command

def main():
    # Initialize components
    init_serial()
    init_vision()
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
        
    last_command_time = 0
    
    print("Starting main loop... Press ESC to exit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
            
        # Detect objects in the frame
        label, bbox, center_x = detect_objects(frame)
        
        if label and label.lower() == "orange":
            x1, y1, x2, y2 = bbox
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
            # Draw center point
            cv2.circle(frame, (center_x, (y1 + y2) // 2), 5, (0, 0, 255), -1)
            
            # Classify into zones: L, C, R
            zone = ""
            if center_x < LEFT_THRESHOLD:
                zone = "L"
            elif center_x > RIGHT_THRESHOLD:
                zone = "R"
            else:
                zone = "C"
                
            # Display zone label
            text = f"{label} Zone: {zone}"
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
            
            # Command sending logic
            current_time = time.time()
            if current_time - last_command_time > COMMAND_DELAY:
                send_command(zone)
                last_command_time = current_time
        
        # Display zone thresholds
        cv2.line(frame, (LEFT_THRESHOLD, 0), (LEFT_THRESHOLD, frame.shape[0]), (255, 0, 0), 2)
        cv2.line(frame, (RIGHT_THRESHOLD, 0), (RIGHT_THRESHOLD, frame.shape[0]), (255, 0, 0), 2)
        
        # Show video feed
        cv2.imshow("Robotic Arm Object Sorting", frame)
        
        # Exit on ESC key
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
            
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
