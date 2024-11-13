import socket
import threading
import time
import matplotlib.pyplot as plt

# Server Configuration
HOST = '172.27.253.41'
PORT = 12345

# Algorithm configurations
ssthresh = 20
leaky_bucket_rate = 5  # packets per second

# Data storage for plotting results
results = {
    "tahoe": {"time": [], "cwnd": [], "losses": 0},
    "reno": {"time": [], "cwnd": [], "losses": 0},
    "leaky_bucket": {"time": [], "cwnd": [], "losses": 0}
}

# Function to handle TCP Tahoe congestion control
def tcp_tahoe(conn, addr):
    cwnd = 1
    packet_count = 0
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            packet_count += 1
            results["tahoe"]["time"].append(packet_count)
            results["tahoe"]["cwnd"].append(cwnd)

            # Send ACK and manage congestion control behavior
            conn.sendall(b'ACK')
            if cwnd < ssthresh:
                cwnd *= 2
            else:
                cwnd += 1

        except socket.timeout:
            # Simulate packet loss, reset CWND
            cwnd = 1
            results["tahoe"]["losses"] += 1
            ssthresh = cwnd // 2

    conn.close()

# Function to handle TCP Reno congestion control
def tcp_reno(conn, addr):
    cwnd = 1
    packet_count = 0
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            packet_count += 1
            results["reno"]["time"].append(packet_count)
            results["reno"]["cwnd"].append(cwnd)

            # Send ACK and manage congestion control behavior
            conn.sendall(b'ACK')
            if cwnd < ssthresh:
                cwnd *= 2
            else:
                cwnd += 1

        except socket.timeout:
            # Fast recovery mode in Reno
            cwnd = ssthresh
            results["reno"]["losses"] += 1

    conn.close()

# Function to handle Leaky Bucket congestion control
def leaky_bucket(conn, addr):
    bucket_size = 10  # maximum packets that can be sent at once
    packet_count = 0
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            packet_count += 1
            results["leaky_bucket"]["time"].append(packet_count)
            if packet_count % leaky_bucket_rate <= bucket_size:
                conn.sendall(b'ACK')
                results["leaky_bucket"]["cwnd"].append(min(bucket_size, packet_count))
            else:
                results["leaky_bucket"]["cwnd"].append(0)  # Simulating packet drop
                results["leaky_bucket"]["losses"] += 1

        except socket.timeout:
            break

    conn.close()

def client_handler(conn, addr):
    # Choose algorithm based on client request
    algorithm = conn.recv(1024).decode()
    print(algorithm)
    if algorithm.lower() == 'tahoepacket':
        tcp_tahoe(conn, addr)
    elif algorithm.lower() == 'renopacket':
        tcp_reno(conn, addr)
    elif algorithm.lower() == 'leaky_bucketpacket':
        leaky_bucket(conn, addr)
    else:
        print(f"[ERROR] Unknown algorithm requested by {addr}: {algorithm}")
        conn.close()

# Server main function
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[INFO] Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            conn.settimeout(1)
            print(f"[INFO] Connection from {addr}")
            threading.Thread(target=client_handler, args=(conn, addr)).start()
            
            
def plot_results():
    # Plot congestion window size over time for each algorithm
    plt.figure(figsize=(12, 6))
    
    # Plot Tahoe results
    plt.subplot(1, 2, 1)
    plt.plot(results["tahoe"]["time"], results["tahoe"]["cwnd"], label='Tahoe', color='blue')
    plt.title('Congestion Window Over Time (Tahoe)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Congestion Window Size')
    plt.grid(True)
    plt.legend()

    # Plot Reno results
    plt.subplot(1, 2, 2)
    plt.plot(results["reno"]["time"], results["reno"]["cwnd"], label='Reno', color='green')
    plt.title('Congestion Window Over Time (Reno)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Congestion Window Size')
    plt.grid(True)
    plt.legend()

    # Show the plots
    plt.tight_layout()
    plt.show()

    # Plot Leaky Bucket results
    plt.figure(figsize=(6, 6))
    plt.plot(results["leaky_bucket"]["time"], results["leaky_bucket"]["cwnd"], label='Leaky Bucket', color='red')
    plt.title('Congestion Window Over Time (Leaky Bucket)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Congestion Window Size')
    plt.grid(True)
    plt.legend()
    plt.show()

    # Plot packet losses for each algorithm
    plt.figure(figsize=(6, 6))
    plt.bar(['Tahoe', 'Reno', 'Leaky Bucket'],
            [results["tahoe"]["losses"], results["reno"]["losses"], results["leaky_bucket"]["losses"]],
            color=['blue', 'green', 'red'])
    plt.title('Packet Losses for Each Algorithm')
    plt.ylabel('Number of Losses')
    plt.show()

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        plot_results()
        print("Server shutting down....")
    
    
