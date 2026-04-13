import cv2
import time
from config import COMMAND_DELAY, LEFT_THRESHOLD, RIGHT_THRESHOLD, CAMERA_INDEX, DEBUG_MODE, CAMERA_FPS, CAMERA_WIDTH, CAMERA_HEIGHT
from vision import init_vision, detect_objects, draw_debug_detections
from serial_comm import init_serial, send_command

def main():
    # Initialize components
    init_serial()
    init_vision()
    
    from vision import get_forced_external_camera
    print("Securing external camera feed (strict 720p check)...")
    cap = get_forced_external_camera()
        
    if cap is None or not cap.isOpened():
        print("Error: Could not find the external webcam.")
        print("Please ensure it is plugged in via USB and run 'python scan_cameras.py'.")
        return

    # Apply USB2.0 PC CAMERA hardware settings
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS,          CAMERA_FPS)

    # Verify we can actually read a frame
    ret, test_frame = cap.read()
    if not ret or test_frame is None:
        print("Error: Camera opened but could not read frames. Run scan_cameras.py to diagnose.")
        cap.release()
        return

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"Camera ready! {actual_w}x{actual_h} @ {actual_fps} FPS")
        
    last_command_time = 0
    # waitKey delay based on camera FPS (1000ms / FPS), min 1ms
    wait_ms = max(1, int(1000 / CAMERA_FPS))
    
    print("Starting main loop... Press ESC to exit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
        
        if DEBUG_MODE:
            # Draw ALL detections so you can see what the model is seeing
            frame = draw_debug_detections(frame)
        else:
            # Detect objects in the frame (orange only)
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
        
        # Exit on ESC key — wait_ms paces loop to match camera FPS
        key = cv2.waitKey(wait_ms) & 0xFF
        if key == 27:
            break
            
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
