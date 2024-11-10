import socket
import threading
import time
import matplotlib.pyplot as plt
import statistics

def make_request(host, port, request_type="GET", path="/crc.html", payload=""):
    """Function to simulate a single client request and return response time."""
    start_time = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        if request_type == "GET":
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"
        elif request_type == "POST":
            request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Length: {len(payload)}\r\n\r\n{payload}"
        s.sendall(request.encode())
        response = s.recv(1024)
        print("Response received:", response.decode())
    end_time = time.time()
    return end_time - start_time  # Return the response time

def run_load_test(host, port, num_clients, delay_between_requests=0.1):
    """Function to run load test by creating multiple client threads."""
    threads = []
    response_times = []

    def client_task():
        response_time = make_request(host, port)
        response_times.append(response_time)

    for _ in range(num_clients):
        thread = threading.Thread(target=client_task)
        thread.start()
        threads.append(thread)
        time.sleep(delay_between_requests)  # Delay to simulate staggered requests

    for thread in threads:
        thread.join()

    return response_times  # Return the collected response times

def evaluate_performance():
    num_clients_list = [1, 5, 10, 20, 50, 100]
    avg_response_times = []
    median_response_times = []
    stddev_response_times = []
    throughputs = []

    for num_clients in num_clients_list:
        start_time = time.time()
        response_times = run_load_test("localhost", 8081, num_clients, delay_between_requests=0)
        end_time = time.time()
        
        # Calculate performance metrics
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        stddev_response_time = statistics.stdev(response_times) if len(response_times) > 1 else 0
        throughput = num_clients / (end_time - start_time)
        
        avg_response_times.append(avg_response_time)
        median_response_times.append(median_response_time)
        stddev_response_times.append(stddev_response_time)
        throughputs.append(throughput)

    # Plot updated performance metrics
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 3, 1)
    plt.plot(num_clients_list, avg_response_times, marker='o')
    plt.xlabel("Number of Clients")
    plt.ylabel("Avg Response Time (s)")
    plt.title("Avg Response Time vs Clients")

    plt.subplot(1, 3, 2)
    plt.plot(num_clients_list, median_response_times, marker='o')
    plt.xlabel("Number of Clients")
    plt.ylabel("Median Response Time (s)")
    plt.title("Median Response Time vs Clients")

    plt.subplot(1, 3, 3)
    plt.plot(num_clients_list, throughputs, marker='o')
    plt.xlabel("Number of Clients")
    plt.ylabel("Throughput (requests/sec)")
    plt.title("Throughput vs Clients")

    plt.tight_layout()
    plt.show()

evaluate_performance()
