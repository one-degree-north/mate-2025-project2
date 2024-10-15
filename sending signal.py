import socket
import subprocess

# List of IR commands that can be sent
cmds = ["POWER", "FREEZE", "VOL_UP", "VOL_DOWN"]

def listen_for_signal():
    # Set up the Raspberry Pi to listen on all available network interfaces
    rpi_host = '0.0.0.0'  # Listen on all available interfaces
    rpi_port = 12345  # Port for the server to listen on
    
    # Create a TCP/IP socket to listen for incoming connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((rpi_host, rpi_port))  # Bind to the specified host and port
        server_socket.listen(1)  # Start listening for one connection at a time
        print("Listening for signal from macOS...")
        
        # Enter a loop to accept connections and handle incoming data
        while True:
            conn, addr = server_socket.accept()  # Accept an incoming connection
            with conn:
                print(f"Connected by {addr}")  # Print the address of the connecting device
                data = conn.recv(1024).decode('utf-8')  # Receive data from the connection and decode it
                
                # Check if the received data is a valid command
                if data in cmds:
                    print("Received power off command. Sending IR signal...")
                    send_ir_signal(data)  # Call the function to send the IR signal

def send_ir_signal(data):
    try:
        # Use the subprocess module to run the "irsend" command via LIRC to send the IR signal
        subprocess.run(["irsend", "SEND_ONCE", "my_remote", data], check=True)
        print("Power signal sent via LIRC.")  # Confirm the signal was sent
    except subprocess.CalledProcessError as e:
        # Handle any errors that occur during the subprocess call
        print(f"Failed to send IR signal: {e}")

if __name__ == "__main__":
    # Start listening for the signal when the script is run
    listen_for_signal()
