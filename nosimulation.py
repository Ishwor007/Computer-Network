import socket
import threading
import time
import random
import matplotlib.pyplot as plt


# Server Configuration
HOST = '172.27.253.41'
PORT = 12345

# Data storage for plotting results
results = {
    "tahoe": {"time": [], "cwnd": [], "losses": 0},
    "reno": {"time": [], "cwnd": [], "losses": 0},
    "custom": {"time": [], "cwnd": [], "losses": 0}
}

# Flag to manage server state
running = True

def tcp_tahoe(conn, addr):
    ssthresh = 20
    cwnd = 1
    packet_count = 0
    while running:
        try:
            data = conn.recv(1024)
            print(f"[SERVER] Received data from {addr}: {data}")

            if not data:
                break
            packet_count += 1
            results["tahoe"]["time"].append(packet_count)
            results["tahoe"]["cwnd"].append(cwnd)

            # Send ACK and manage congestion control behavior
            conn.sendall(b'ACK')

            # Congestion Control
            if cwnd < ssthresh:
                cwnd *= 2  # Slow start
            else:
                cwnd += 1  # Congestion avoidance

            # If no ACK is received (simulated loss scenario), reduce cwnd
            if data != b'ACK':
                cwnd = 1  # Reset CWND on loss
                results["tahoe"]["losses"] += 1
                ssthresh = max(cwnd // 2, 2)

        except socket.timeout:
            break

    conn.close()

def tcp_reno(conn, addr):
    ssthresh = 20
    cwnd = 1
    packet_count = 0
    print("outside reno try")
    while running:
        try:
            print("inside reno try")
            data = conn.recv(1024)
            print(f"[SERVER] Received data from {addr}: {data}")

            if not data:
                break
            packet_count += 1
            results["reno"]["time"].append(packet_count)
            results["reno"]["cwnd"].append(cwnd)

            # Send ACK and manage congestion control behavior
            conn.sendall(b'ACK')

            # Congestion Control
            if cwnd < ssthresh:
                cwnd *= 2  # Slow start
            else:
                cwnd += 1  # Congestion avoidance

            # If no ACK is received (simulated loss scenario), reduce cwnd
            if data != b'ACK':
                cwnd = ssthresh  # Fast recovery mode
                results["reno"]["losses"] += 1

        except socket.timeout:
            break

    conn.close()

def custom_algorithm(conn, addr):
    ssthresh = 20
    cwnd = 1
    packet_count = 0
    while running:
        try:
            data = conn.recv(1024)
            print(f"[SERVER] Received data from {addr}: {data}")

            if not data:
                break
            packet_count += 1
            results["custom"]["time"].append(packet_count)
            results["custom"]["cwnd"].append(cwnd)

            # Send ACK and manage congestion control behavior
            conn.sendall(b'ACK')

            # Custom Congestion Control (smaller growth)
            if cwnd < ssthresh:
                cwnd *= 2  # Slow start
            else:
                cwnd += 1 / cwnd  # Custom Congestion Avoidance

            # If no ACK is received (simulated loss scenario), reduce cwnd
            if data != b'ACK':
                cwnd = max(1, cwnd - 3)  # Custom loss handling
                results["custom"]["losses"] += 1

        except socket.timeout:
            break

    conn.close()
    
def client_handler(conn, addr):
    algorithm = conn.recv(1024).decode()
    print(algorithm)
    if algorithm.lower() == 'tahoepacket':
        tcp_tahoe(conn, addr)
    elif algorithm.lower() == 'renopacket':
        tcp_reno(conn, addr)
    elif algorithm.lower() == 'custompacket':
        custom_algorithm(conn, addr)
    else:
        print(f"[ERROR] Unknown algorithm requested by {addr}: {algorithm}")
        conn.close()

def start_server():
    global running
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen(5)
            print(f"[INFO] Server listening on {HOST}:{PORT}")

            while running:
                conn, addr = server_socket.accept()
                conn.settimeout(10)
                print(f"[INFO] Connection from {addr}")
                threading.Thread(target=client_handler, args=(conn, addr)).start()

    except KeyboardInterrupt:
        print("\n[INFO] Server interrupted by user. Shutting down...")
        running = False
        plot_results()
    finally:
        print("Server shutting down.")

def plot_results():
    # Plot congestion window size over time for each algorithm
    plt.figure(figsize=(12, 6))
    # Plot Tahoe results
    plt.subplot(1, 3, 1)
    plt.plot(results["tahoe"]["time"], results["tahoe"]["cwnd"], label='Tahoe', color='blue')
    plt.title('Congestion Window Over Time (Tahoe)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Congestion Window Size')
    plt.grid(True)
    plt.legend()

    # Plot Reno results
    plt.subplot(1, 3, 2)
    plt.plot(results["reno"]["time"], results["reno"]["cwnd"], label='Reno', color='green')
    plt.title('Congestion Window Over Time (Reno)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Congestion Window Size')
    plt.grid(True)
    plt.legend()

    # Plot Custom results
    plt.subplot(1, 3, 3)
    plt.plot(results["custom"]["time"], results["custom"]["cwnd"], label='Custom Algorithm', color='red')
    plt.title('Congestion Window Over Time (Custom)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Congestion Window Size')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()

    # Plot comparison of packet losses
    plt.figure(figsize=(6, 6))
    plt.plot(['Tahoe', 'Reno', 'Custom'],
            [results["tahoe"]["losses"], results["reno"]["losses"], results["custom"]["losses"]])
    plt.title('Packet Losses for Each Algorithm')
    plt.ylabel('Number of Losses')
    plt.show()

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        plot_results()
    finally:
        print("Server shutting down after plotting result.")



