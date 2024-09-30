import openai
import speech_recognition as sr
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to send LIRC command
def send_lirc_command(remote_name, button_name):
    command = f"irsend SEND_ONCE {remote_name} {button_name}"
    os.system(command)
    print(f"Sent command: {command}")

# Function to be called when voice is recognized
def my_function():
    print("Voice command recognized! Sending LIRC command...")
    # Replace 'my_remote' and 'KEY_POWER' with your actual remote name and button
    send_lirc_command("my_remote", "KEY_POWER")

# Function to make a request to OpenAI's API using the new ChatCompletion
def ask_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or any available model, like gpt-4 if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
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

            # If the recognized command contains "activate", call the function to send LIRC command
            if "activate" in command.lower():
                my_function()

            # If the recognized command contains "openai", send a request to OpenAI
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
    while True:
        listen_and_process_voice_command()


