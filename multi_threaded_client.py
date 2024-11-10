from socket import *
import threading

# Function to send a GET request to the server
def send_get_request(host, port, file_path, client_id):
    try:
        with socket(AF_INET, SOCK_STREAM) as clientSocket:
            # Connect to the server
            clientSocket.connect((host, port))
        
            # Formulate the GET request
            request = (f"GET /{file_path} HTTP/1.1\r\n"
                       f"Host: {host}\r\n"
                       f"Client-Id: {client_id}\r\n"
                       f"Connection: keep-alive\r\n\r\n")
            clientSocket.send(request.encode('utf-8'))
        
            # Managing Server's Long Response
            response = ""
            while True:
                part = clientSocket.recv(4096).decode('utf-8')
                if not part:
                    break
                response += part

        print(f"Client {client_id} Response For GET:\n{response}\n" + "_"*50)

    except Exception as e:
        print(f"Client {client_id} encountered an error: {e}")

# Function to send a POST request to the server
def send_post_request(host, port, file_data, client_id):
    with socket(AF_INET, SOCK_STREAM) as clientSocket:
        # Connect to the server
        clientSocket.connect((host, port))
        
        # Formulate the POST request
        request = (f"POST / HTTP/1.1\r\n"
                   f"Host: {host}\r\n"
                   f"Client-Id: {client_id}\r\n"
                   f"Connection: keep-alive\r\n\r\n")
        clientSocket.send(request.encode('utf-8'))
        
        # Wait for the server's OK response
        response = clientSocket.recv(1024).decode('utf-8')
        print(f"Client {client_id} Response from server for POST:\n{response}\n" + "_"*50)
        
        # Send the file data
        clientSocket.send(file_data.encode('utf-8'))
        
        # Optionally, receive the server's final acknowledgment or response (if implemented in the server)
        response = clientSocket.recv(4096).decode('utf-8')
        print(f"Client {client_id} - Response from server after sending file data:\n{response}\n" + "_"*50)


def not_allowed(host, port, client_id):
    with socket(AF_INET, SOCK_STREAM) as clientSocket:
        # Connect to the server
        clientSocket.connect((host, port))
        
        # Formulate the POST request
        request = (f"random text for\r\n"
                   f"not allowed method\r\n"
                   f"Client-Id: {client_id}\r\n"
                   f"Connection: keep-alive\r\n\r\n")
        clientSocket.send(request.encode('utf-8'))
        
        # Wait for the server's OK response
        response = clientSocket.recv(1024).decode('utf-8')
        print(f"Client {client_id} - Response from server for not allowed method:\n{response}\n"+ "_"*50)


# Function to start multiple client threads
def run_threaded_requests(host, port, num_clients):
    threads = []
    for i in range(num_clients):
        # Initialize the client threads for GET, POST and not allowed requests
        if i % 3 == 0:
            file_path = "get_test.txt"
            thread = threading.Thread(target=send_get_request, args=(host, port, file_path, i))
        elif i % 3 == 1:
            file_data = f"This is the content of the uploaded file from client {i}."
            thread = threading.Thread(target=send_post_request, args=(host, port, file_data, i))
        else:
            file_data = f"This is not needed for client {i}."
            thread = threading.Thread(target=not_allowed, args=(host, port, i))

        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8080
    num_clients = 10
    
    run_threaded_requests(host, port, num_clients)
