# serial_bridge.py
import serial
import time


def main():
    # Configure ports (adjust as needed)
    ARDUINO_PORT = "/dev/ttyACM0"  # CNC Arduino
    ESP32_PORT = "/dev/ttyUSB0"  # ESP32 Pendant
    BAUD_RATE = 115200

    try:
        # Open serial connections
        arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        esp32 = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)

        print(f"Forwarding {ESP32_PORT} → {ARDUINO_PORT}...")

        while True:
            if esp32.in_waiting:
                cmd = esp32.readline().decode().strip()
                print(f"Pendant: {cmd}")
                arduino.write((cmd + '\n').encode())  # Forward to CNC

            time.sleep(0.01)  # Reduce CPU usage

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()