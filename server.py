import socket
import matplotlib.pyplot as plt
import time
import random

# Server settings
SERVER_IP = '172.27.253.41'  # Listen on all network interfaces
PORT = 12345  # Port to listen on

# Initialize congestion control variables
cwnd = 1
threshold = 10
MAX_CWND = 100
packet_loss_probability = 0.1  # 10% chance of packet loss
cwnd_history = []

# Set up UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, PORT))
print("Server is ready and listening...")

start_time = time.time()

try:
    while True:
        # Receive packet
        
        print("packet recieve")
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        elapsed_time = time.time() - start_time
        packet_loss = random.random() < packet_loss_probability

        if not packet_loss:
            # Increase cwnd according to TCP Tahoe
            print("packet not loss")
            if cwnd < threshold:
                cwnd = min(cwnd * 2, MAX_CWND)  # Slow Start
            else:
                cwnd += 1  # Congestion Avoidance
        else:
            print(f"Packet loss detected at {elapsed_time:.2f}s!")
            threshold = max(cwnd // 2, 1)
            cwnd = 1  # Reset CWND after loss

        cwnd_history.append(cwnd)
        print(f"Time: {elapsed_time:.2f}s, CWND: {cwnd}, Threshold: {threshold}")

except KeyboardInterrupt:
    print("Server shutting down...")

# Plot the CWND history after stopping the server
plt.plot(cwnd_history, label="CWND")
plt.axhline(y=threshold, color='r', linestyle='--', label="Threshold")
plt.xlabel("Time Steps")
plt.ylabel("Congestion Window Size (CWND)")
plt.title("TCP Tahoe Congestion Control Simulation")
plt.legend()
plt.show()
plt.savefig("cwnd_plot.png")

