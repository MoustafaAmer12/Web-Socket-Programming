from socket import *
import threading
import os
import mimetypes

def serve_client(connectionSocket):
    # Set Timeout for each connectionSocket
    connectionSocket.settimeout(10)
    try:
        while True:
            try:
                request = connectionSocket.recv(1024).decode('utf-8')
                
                if not request:
                    break

                # Print out the received command and headers
                print("Received request:")
                print(request + "\n" + "_"*50 + "\n")

                # Parse the request line and headers
                lines = request.split('\r\n')
                request_line = lines[0]
                headers = dict(line.split(': ', 1) for line in lines[1:] if ': ' in line)
                method, path, _ = request_line.split()
                client_id = headers.get("Client-ID", "Unknown")

                # Handle GET requests
                if method == 'GET':
                    filename = path.lstrip('/')
                    if os.path.exists(filename):
                        content_type, _ = mimetypes.guess_type(filename)
                        content_type = content_type or 'application/octet-stream'
                        
                        with open(filename, 'rb') as f:
                            file_data = f.read()
                        
                        if(filename.endswith(".png")):
                            response = file_data
                        else:
                            resBody = file_data
                            response = (
                                f"HTTP/1.1 200 OK\r\n"
                                f"Client-ID: {client_id}\r\n"
                                f"Content-Type: {content_type}\r\n"
                                f"Content-Length: {len(resBody)}\r\n"
                                f"Connection: keep-alive\r\n\r\n"
                            )
                            response = response.encode('utf-8') + resBody
                    else:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n".encode('utf-8')

                # Handle POST requests
                elif method == 'POST':
                    response = (
                        f"HTTP/1.1 200 OK\r\n"
                        f"Client-ID: {client_id}\r\n"
                        f"Connection: keep-alive\r\n\r\n"
                    ).encode('utf-8')
                    connectionSocket.sendall(response)
                    
                    # Receive file data for POST
                    file_data = connectionSocket.recv(4096)
                    with open(f"{path[1:]}", 'wb') as f:
                        f.write(file_data)
                    response = "File uploaded successfully.".encode('utf-8')

                # Handle other requests
                else:
                    response = (
                        f"HTTP/1.1 405 Method Not Allowed\r\n"
                        f"Client-ID: {client_id}\r\n"
                        f"Connection: keep-alive\r\n\r\n"
                    ).encode('utf-8')

                # Send response to client
                connectionSocket.sendall(response)

                # Close the connection if not keep-alive
                if headers.get("Connection", "").lower() != "keep-alive":
                    print(f"Closing connection for client {client_id}.")
                    break

            except timeout:
                print(f"Connection timed out for client {client_id}.")
                break

            except Exception as e:
                print(f"Error: {e}")
                break

    finally:
        print("Closing connection.")
        connectionSocket.close()

# Handle Server Connections
def start_server(port=8080):
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(('127.0.0.1', port))
    server.listen(10)
    print(f"Server listening on port {port}")

    while True:
        connectionSocket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=serve_client, args=(connectionSocket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
