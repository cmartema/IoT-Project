import socket
import signal
import sys

def signal_handler(sig, frame):
    print("Ctrl+C pressed. Closing the server.")
    server_socket.close()
    sys.exit(0)

# Define the server's IP address and port
host = '10.206.96.143'  # localhost
port = 54235         # choose an available port

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind((host, port))

# Listen for incoming connections (max queue size is specified)
server_socket.listen(5)

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

print(f"Server listening on {host}:{port}")

try:
    while True:
        # Wait for a client to connect
        client_socket, client_address = server_socket.accept()

        print(f"Connection from {client_address}")

        # Send a welcome message to the client
        message = "Welcome to the server!"
        client_socket.send(message.encode('utf-8'))

        # Receive data from the client
        data = client_socket.recv(1024).decode('utf-8')
        print(f"Received data: {data}")

        # Close the connection with the client
        client_socket.close()

except KeyboardInterrupt:
    print("Ctrl+C pressed. Closing the server.")
    server_socket.close()
    sys.exit(0)