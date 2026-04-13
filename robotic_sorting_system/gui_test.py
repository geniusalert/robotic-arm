import tkinter as tk
from tkinter import scrolledtext, ttk
import cv2
from PIL import Image, ImageTk
import serial
import time
from config import COM_PORT, BAUD_RATE, CAMERA_INDEX

class RobotTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robotic Arm Tester & Calibrator")
        self.root.geometry("800x650")
        
        # State variables
        self.ser = None
        self.cap = None
        self.is_running = True
        
        self.setup_ui()
        self.init_hardware()
        
        # Start video loop
        self.update_video()

    def setup_ui(self):
        # Top Frame: Camera Feed
        self.video_frame = tk.LabelFrame(self.root, text="Live Camera Feed", padx=10, pady=10)
        self.video_frame.pack(pady=10)
        
        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack()
        
        # Middle Frame: Controls
        self.control_frame = tk.LabelFrame(self.root, text="Manual Controls", padx=10, pady=10)
        self.control_frame.pack(pady=10)
        
        btn_left = ttk.Button(self.control_frame, text="Pick Left (L)", command=lambda: self.send_command("L"))
        btn_left.grid(row=0, column=0, padx=10)
        
        btn_center = ttk.Button(self.control_frame, text="Pick Center (C)", command=lambda: self.send_command("C"))
        btn_center.grid(row=0, column=1, padx=10)
        
        btn_right = ttk.Button(self.control_frame, text="Pick Right (R)", command=lambda: self.send_command("R"))
        btn_right.grid(row=0, column=2, padx=10)
        
        # Status/Log Frame
        self.log_frame = tk.LabelFrame(self.root, text="System Logs & Errors", padx=10, pady=10)
        self.log_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.status_lbl = tk.Label(self.log_frame, text="Status: Initializing...", font=("Arial", 12, "bold"))
        self.status_lbl.pack(pady=5)
        
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=8, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
    def init_hardware(self):
        # Init Camera
        from vision import get_forced_external_camera
        try:
            self.cap = get_forced_external_camera()
            if self.cap is None or not self.cap.isOpened():
                self.log(f"ERROR: Could not secure external 720p Camera feed.")
                self.status_lbl.config(text="Status: Camera Error | Hardware Disconnected", fg="red")
            else:
                self.log("External Camera initialized successfully.")
                self.status_lbl.config(text="Status: Camera OK", fg="blue")
        except Exception as e:
            self.log(f"ERROR: Cannot initialize camera: {e}")
            
        # Init Serial
        try:
            self.ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
            self.log(f"Connected to Arduino on {COM_PORT}")
            # Merge statuses if both are working
            if self.cap and self.cap.isOpened():
                self.status_lbl.config(text=f"Status: Connected to {COM_PORT} & Camera OK", fg="green")
            else:
                self.status_lbl.config(text=f"Status: Connected to {COM_PORT} & Camera Error", fg="orange")
        except Exception as e:
            self.log(f"ERROR: Serial connect failed on {COM_PORT}. Check connection. Err: {e}")
            if self.cap and self.cap.isOpened():
                self.status_lbl.config(text="Status: Camera OK, Arduino Disconnected", fg="orange")

    def send_command(self, cmd):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write((cmd + "\n").encode('utf-8'))
                self.log(f"SENT: {cmd}")
            except Exception as e:
                self.log(f"ERROR: Failed to send '{cmd}': {str(e)}")
        else:
            self.log(f"ERROR: Cannot send '{cmd}'. Arduino not connected via {COM_PORT}.")

    def update_video(self):
        if self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Resize to fit GUI comfortably
                frame = cv2.resize(frame, (640, 480))
                # Convert BGR to RGB for Tkinter display compatibility
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            else:
                self.log("ERROR: Interruption in camera feed.")
        
        # Continuously update the frame
        if self.is_running:
            self.root.after(30, self.update_video)
            
    def close_app(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotTesterApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_app)
    root.mainloop()
