import socket
import signal
import sys

def signal_handler(sig, frame):
    print("Ctrl+C pressed. Closing the server.")
    server_socket.close()
    sys.exit(0)

# Define the server's IP address and port
ip = '10.207.50.131'  # localhost
port = 54235         # choose an available port
BUFLEN = 512

# sockaddr = socket.getaddrinfo('127.0.0.1', 80)[0][-1]
ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ListenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# ListenSocket.bind(sockaddr)
ListenSocket.bind((ip, port))
ListenSocket.listen(2)
print(f'Enable server, Listen on {port}')

DataSocket, addr = ListenSocket.accept()
print('Accept a client', addr)
module = 1
info = ''
while True:
    tosent = input(">>")
    DataSocket.send(tosent.encode())

    received = DataSocket.recv(BUFLEN)
    print(received.decode())

DataSocket.close()
ListenSocket.close()