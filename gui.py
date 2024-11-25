import serial
import tkinter as tk
from tkinter import ttk

# Function to send a command to the Arduino
def send_command(channel, value):
    if ser:
        command = f"C{channel} {value}\n"
        try:
            ser.write(command.encode())
            print(f"Sent: {command.strip()}")
        except Exception as e:
            print(f"Error sending command: {e}")
    else:
        print("Serial connection not established.")

# Function to reset the Arduino and sliders
def reset_device():
    if ser:
        try:
            # Send the reset command to the Arduino
            ser.write(b"R\n")
            print("Sent: R")
        except Exception as e:
            print(f"Error sending reset command: {e}")
    else:
        print("Serial connection not established.")

    # Reset all sliders to 1500
    for i in range(1, 7):
        sliders[i].set(1500)  # Set slider to middle value
        if ser:
            send_command(i, 1500)  # Send the reset value to Arduino

# Create the serial connection
ser = None
try:
    ser = serial.Serial('COM7', 115200, timeout=1)  # Replace 'COM3' with your Arduino's port
    print("Serial connection established")
except Exception as e:
    print(f"Error connecting to serial device: {e}")

# Create the GUI
root = tk.Tk()
root.title("Arduino Channel Controller")

# Frame for the sliders
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0)

# Slider controls for each channel
sliders = {}
for i in range(1, 7):
    ttk.Label(frame, text=f"Channel {i}").grid(row=i - 1, column=0, padx=5, pady=5)
    sliders[i] = tk.Scale(
        frame,
        from_=1000,
        to=2000,
        orient=tk.HORIZONTAL,
        length=300,
        command=lambda value, channel=i: send_command(channel, int(float(value)))
    )
    sliders[i].set(1500)  # Set default value to the middle
    sliders[i].grid(row=i - 1, column=1, padx=5, pady=5)

# Reset button
reset_button = ttk.Button(root, text="Reset", command=reset_device)
reset_button.grid(row=1, column=0, pady=10)

# Run the application
try:
    root.mainloop()
finally:
    if ser:
        ser.close()
        print("Serial connection closed")