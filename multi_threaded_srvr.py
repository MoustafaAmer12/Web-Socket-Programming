from socket import *
import threading
import os
import mimetypes

def handle_request(connectionSocket):
    # Set Timeout for each connectionSocket
    connectionSocket.settimeout(60)
    client_id = None

    # Receives Multiple requests from the client and manages them
    while True:
        try:
            request = connectionSocket.recv(1024).decode('utf-8')
            if not request:
                break

            # Print out the received command and headers
            print("Received request:")
            print(request + "\n" + "_"*50 + "\n")

            # Parse the request line
            lines = request.split('\r\n')
            request_line = lines[0]
            client_id = lines[2]
            method, path, _ = request_line.split()

            # Handle GET requests
            if method == 'GET':
                filename = path.lstrip('/')
                if os.path.exists(filename):
                    content_type, _ = mimetypes.guess_type(filename)
                    content_type = content_type or 'application/octet-stream'
                    
                    with open(filename, 'rb') as f:
                        file_data = f.read()
                    
                    resBody = file_data
                    response_headers = (
                        f"HTTP/1.1 200 OK\r\n"
                        f"{client_id}\r\n"
                        f"Content-Type: {content_type}\r\n"
                        f"Content-Length: {len(resBody)}\r\n"
                        f"Connection: keep-alive\r\n\r\n"
                    )
                    response = response_headers.encode('utf-8') + resBody
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"

            # Handle POST requests
            elif method == 'POST':
                response_headers = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"{client_id}\r\n"
                    f"Connection: keep-alive\r\n\r\n"
                )
                connectionSocket.send(response_headers.encode('utf-8'))
                
                file_data = connectionSocket.recv(4096)
                with open("uploaded_file.txt", 'wb') as f:
                    f.write(file_data)
                response = b'' # No need for response acknowlegement

            # Handle other requests
            else:
                response = (
                    f"HTTP/1.1 405 Method Not Allowed\r\n"
                    f"{client_id}\r\n"
                    f"Connection: close\r\n\r\n"
                ).encode('utf-8')
                connectionSocket.send(response)
                break

            # Send response to client
            connectionSocket.send(response.encode('utf-8'))

            if "Connection: keep-alive" not in request:
                break
        
        except timeout:
            print(f"Connection timed out for client {client_id}.")
            break

        except Exception as e:
            print(f"Error: {e}")
            break

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
        client_handler = threading.Thread(target=handle_request, args=(connectionSocket,))
        client_handler.start()


if __name__ == "__main__":
    start_server()
