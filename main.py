import openai
import speech_recognition as sr
import os
import sys

# Set your API key securely (use environment variables instead of hardcoding)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to send LIRC command
def send_lirc_command(remote_name, button_name):
    command = f"irsend SEND_ONCE {remote_name} {button_name}"
    os.system(command)
    print(f"Sent command: {command}")

# Function to be called when voice is recognized
def my_function():
    print("Voice command recognized! Sending LIRC command...")
    send_lirc_command("my_remote", "KEY_POWER")

# Function to make a request to OpenAI API (optional use case)
def ask_openai(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

# Initialize recognizer
r = sr.Recognizer()

def listen_and_process_voice_command():
    # Start listening for voice commands
    with sr.Microphone() as source:
        print("Listening for your command...")
        audio = r.listen(source)

        try:
            # Recognize speech using Google Speech Recognition
            command = r.recognize_google(audio)
            print(f"You said: {command}")

            # Process recognized command (voice-controlled LIRC)
            if "activate" in command.lower():
                my_function()

            # Optionally, send a prompt to OpenAI API
            elif "openai" in command.lower():
                openai_response = ask_openai("What is the capital of France?")
                if openai_response:
                    print(f"OpenAI response: {openai_response}")

        except sr.UnknownValueError:
            print("Could not understand the audio")
        except sr.RequestError:
            print("Error with the recognition service")

# Main loop to continuously listen and process voice commands
if __name__ == "__main__":
    print("Starting voice command to LIRC controller and OpenAI API...")
    
    # Check if API key is set
    if openai.api_key is None:
        print("Error: OpenAI API key not set.")
        sys.exit(1)
    
    # Continuously listen for voice commands
    while True:
        listen_and_process_voice_command()
