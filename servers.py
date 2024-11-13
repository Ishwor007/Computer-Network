import socket
import random

# Set up server parameters
server_ip = '172.27.253.41'
server_port = 12345
loss_probability = 0.1  # 10% chance of dropping a packet to simulate congestion

# Initialize and bind the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_ip, server_port))

print(f"Server started at {server_ip}:{server_port}")

while True:
    # Receive a packet from the client
    data, client_address = server_socket.recvfrom(1024)
    packet_num = int(data.decode())

    # Simulate packet loss
    if random.random() < loss_probability:
        print(f"Packet {packet_num} lost.")
        continue  # Do not send ACK for this packet

    # Send ACK for received packet
    print(f"Received packet {packet_num}. Sending ACK.")
    server_socket.sendto(f"ACK {packet_num}".encode(), client_address)

