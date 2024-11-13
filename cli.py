import socket
import time
import signal
import sys

# Server Configuration
SERVER_IP = '172.27.253.41'
PORT = 12345

# Global flag to manage keyboard interrupt
running = True

def signal_handler(sig, frame):
    global running
    running = False
    print("\n[INFO] Stopping packet transmission...")

# Client function to send packets based on specified algorithm
def client_send_packets(algorithm):
    while running:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((SERVER_IP, PORT))
                s.sendall(algorithm.encode())  # Send chosen algorithm to server
                s.settimeout(1)  # Set a short timeout for testing

                packet_count = 0
                while running:
                    try:
                        s.sendall(b'Packet')
                        ack = s.recv(1024)
                        if ack == b'ACK':
                            print(f"Packet {packet_count} sent, ACK received")
                        packet_count += 1
                        time.sleep(0.5)

                    except socket.timeout:
                        print(f"Packet {packet_count} lost!")
                        packet_count += 1

        except (ConnectionAbortedError, ConnectionResetError, socket.timeout) as e:
            print(f"[ERROR] Connection error: {e}. Reconnecting...")
            time.sleep(1)  # Wait a moment before trying to reconnect

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    algorithm = input("Enter TCP algorithm (Tahoe/Reno/Leaky_Bucket): ").strip().lower()
    if algorithm in ["tahoe", "reno", "leaky_bucket"]:
        client_send_packets(algorithm)
    else:
        print("Unsupported algorithm")
