import os
import queue
import sounddevice as sd
import vosk
import json
import socket
import time

# Set the path to the Vosk model
MODEL_PATH = "vosk-model-en-us-0.22"

# Load the Vosk model
if not os.path.exists(MODEL_PATH):
    # Check if the model path exists, if not, prompt the user to download it
    print(f"Model not found at {MODEL_PATH}. Please download it from https://alphacephei.com/vosk/models.")
    exit(1)

model = vosk.Model(MODEL_PATH)  # Load the model from the specified path

# Create a queue to store the audio data
q = queue.Queue()

# Audio callback function
def callback(indata, frames, time, status):
    if status:
        # If there is any status, print it (e.g., errors or warnings)
        print(status)
    q.put(bytes(indata))  # Put the audio data into the queue

# Function to send a signal to the Raspberry Pi
def send_signal_to_rpi(message):
    rpi_address = 'pi2.local'  # Address of the Raspberry Pi
    rpi_port = 12345  # Port for communication with the Raspberry Pi

    try:
        # Create a socket to connect to the Raspberry Pi
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((rpi_address, rpi_port))  # Connect to the Raspberry Pi using its address and port
        sock.sendall(message.encode('utf-8'))  # Send the message (command) to the Raspberry Pi
        print(f"Signal '{message}' sent to Raspberry Pi.")  # Confirm that the signal was sent
    except Exception as e:
        # Handle any exceptions (e.g., connection issues)
        print(f"Failed to send signal: {e}")
    finally:
        sock.close()  # Close the socket after the operation

# Initialize the speech recognizer
recognizer = vosk.KaldiRecognizer(model, 16000)  # Set up the Vosk recognizer with the model and sample rate

# Command dictionary mapping spoken words to IR commands
cmds = {
    "vector power": "POWER",
    "vector freeze": "FREEZE",
    "vector volume up": "VOL_UP",
    "vector volume down": "VOL_DOWN"
}

# Store the last recognized command and the last recognized time
last_recognized_cmd = None  # Keeps track of the last command that was recognized
last_recognized_time = 0  # Keeps track of the time when the last command was recognized
COOLDOWN_PERIOD = 5  # Cooldown period in seconds to prevent repeated commands

# Function to start listening and recognizing speech
def recognize_speech():
    global last_recognized_cmd, last_recognized_time  # Access global variables for tracking commands
    print("Listening...")  # Print a message indicating that the system is listening for speech

    # Open the audio stream with sounddevice
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            # Get audio data from the queue
            data = q.get()
            if recognizer.AcceptWaveform(data):
                # If a complete speech result is available, process it
                result = json.loads(recognizer.Result())["text"]  # Parse the recognized speech result
                print(f"Recognized: {result}")  # Print the recognized text

                current_time = time.time()  # Get the current time
                # Check if the recognized command is new and if the cooldown period has passed
                for cmd in cmds:
                    if cmd in result and (cmd != last_recognized_cmd or current_time - last_recognized_time >= COOLDOWN_PERIOD):
                        # Send the command to the Raspberry Pi if conditions are met
                        send_signal_to_rpi(cmds[cmd])
                        last_recognized_cmd = cmd  # Update last recognized command
                        last_recognized_time = current_time  # Update the time of the last recognized command
            else:
                # You can choose to skip printing partial results to reduce noise
                pass

if __name__ == "__main__":
    recognize_speech()  # Start the speech recognition process
