import serial
import time
from config import COM_PORT, BAUD_RATE

ser = None

def init_serial(port=COM_PORT, baud_rate=BAUD_RATE):
    """
    Initializes serial connection to Arduino.
    """
    global ser
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset upon connection
        print(f"Connected to Arduino on {port}")
        return True
    except Exception as e:
        print(f"Error opening serial port {port}: {e}")
        return False

def send_command(cmd: str):
    """
    Sends a command to the Arduino terminating with a newline.
    Adds a small delay to prevent flooding the serial port.
    """
    global ser
    if ser and ser.is_open:
        try:
            ser.write((cmd + "\n").encode('utf-8'))
            print(f"Sent command: {cmd}")
            time.sleep(0.05)  # Small delay after sending command to prevent flooding
            return True
        except Exception as e:
            print(f"Failed to send command: {e}")
            return False
    else:
        print("Serial connection is not open.")
        return False
