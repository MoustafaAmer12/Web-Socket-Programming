from socket import *
import threading
import time

def send_get_request(client_socket, path, client_id="TestClient"):
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: 127.0.0.1\r\n"
        f"Client-ID: {client_id}\r\n"
        f"Connection: keep-alive\r\n\r\n"
    )
    client_socket.sendall(request.encode('utf-8'))
    response = client_socket.recv(4096).decode('utf-8')
    print(f"{client_id} GET response:\n", response + "\n" + "_"*50 + "\n")

def send_post_request(client_socket, path, data, client_id="TestClient"):
    request = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: 127.0.0.1\r\n"
        f"Client-ID: {client_id}\r\n"
        f"Content-Length: {len(data)}\r\n"
        f"Connection: keep-alive\r\n\r\n"
    )
    client_socket.sendall(request.encode('utf-8'))
    response = client_socket.recv(4096).decode('utf-8')
    print(f"{client_id} POST response:\n", response + "\n" + "_"*50 + "\n")

    client_socket.sendall(data)
    file_ack = client_socket.recv(4096).decode('utf-8')
    print(f"{client_id} File Post Acknowledgenent:\n", file_ack + "\n" + "_"*50 +   "\n")

    

def send_anonymous_request(client_socket, path, client_id):
    request = (
        f"RANDOM {path} HTTP/1.1\r\n"
        f"Host: 127.0.0.1\r\n"
        f"Client-ID: {client_id}\r\n"
        f"Connection: keep-alive\r\n\r\n"
    )
    client_socket.sendall(request.encode('utf-8'))
    response = client_socket.recv(4096).decode('utf-8')
    print(f"{client_id} Anonymous request:\n", response + "\n" + "_"*50 + "\n")

def client_sequence(client_id):
    # Connect to the server
    server_host = '127.0.0.1'
    server_port = 8080
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    
    try:
        # Send a GET request for an existing file
        send_get_request(client_socket, "/get_test.txt", client_id)

        # Wait briefly to simulate separate requests
        time.sleep(1)
        
        # Send a GET request for a non-existent file
        send_get_request(client_socket, "/example.txt", client_id)

        # Wait briefly to simulate separate requests
        time.sleep(1)
        
        # Send a POST request with some data
        data = b"Sample data for POST request."
        send_post_request(client_socket, "/upload_file.txt", data, client_id)

        # Wait briefly to simulate separate requests
        time.sleep(1)
        
        # Send another GET request to ensure the connection persists
        send_anonymous_request(client_socket, "/get_test.txt", client_id)
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Close the connection
        client_socket.close()
        print(f"{client_id} connection closed.")

def main():
    # Number of client threads to simulate
    num_clients = 5
    threads = []

    for i in range(num_clients):
        client_id = f"Client-{i+1}"
        thread = threading.Thread(target=client_sequence, args=(client_id,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    print("All client threads completed.")

if __name__ == "__main__":
    main()
