import socket
import threading
import os

class SimpleHTTPServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.timeout_idle = 10  # Default idle timeout (seconds)
        self.timeout_busy = 5   # Shorter timeout for busy conditions (seconds)
        self.connections = []   # Track active connections for dynamic timeout
        self.lock = threading.Lock()  # Ensure thread-safe access to connections list

    def handle_client(self, client_socket):
        with client_socket:
            # Add client to active connections
            with self.lock:
                self.connections.append(client_socket)

            print(f"Active connections: {len(self.connections)}")
            print(f"Clients: {self.connections}")
            print(f"Timeout: {self.get_dynamic_timeout()}")
            try:
                while True:
                    # Set the timeout dynamically based on server load
                    client_socket.settimeout(self.get_dynamic_timeout())
                    try:
                        # Receive client request
                        request = client_socket.recv(1024)
                        if not request:
                            break

                        # Process and respond to the request
                        response = self.process_request(request)
                        client_socket.sendall(response)

                        # Check if the client requested to close the connection
                        if b"Connection: close" in request:
                            break

                    except socket.timeout:
                        print("Connection timed out.")
                        break
                    except Exception as e:
                        print(f"Error: {e}")
                        break
            finally:
                # Remove client from active connections when done
                with self.lock:
                    self.connections.remove(client_socket)

    def get_dynamic_timeout(self):
        """Adjust timeout based on server load."""
        with self.lock:
            num_connections = len(self.connections)
        return self.timeout_busy if num_connections > 5 else self.timeout_idle

    def process_request(self, request):
        """Process a single HTTP request and return the response."""
        print("Received request:", request.decode())
        
        # Parse the request line
        lines = request.decode().splitlines()
        if not lines:
            return self.build_response(400, "Bad Request")

        request_line = lines[0]
        method, path, _ = request_line.split()[:3]

        # Handle GET requests
        if method == "GET":
            return self.handle_get(path)
        
        # Handle POST requests
        elif method == "POST":
            return self.handle_post()
        
        # Method not allowed
        else:
            return self.build_response(405, "Method Not Allowed")

    def handle_get(self, path):
        """Handle GET requests by serving files or returning a 404."""
        if path == "/":
            path = "/index.html"  # Default to index.html if root is requested

        # Check if the requested file exists
        filepath = "." + path
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                body = f.read()
            return self.build_response(200, "OK", body)
        else:
            return self.build_response(404, "Not Found", "404 Not Found")

    def handle_post(self):
        """Handle POST requests by acknowledging receipt."""
        body = "POST request received"
        return self.build_response(200, "OK", body)

    def build_response(self, status_code, status_text, body=""):
        """Construct an HTTP response based on the status code and body."""
        response_lines = [
            f"HTTP/1.1 {status_code} {status_text}",
            "Content-Type: text/html",
            f"Content-Length: {len(body)}",
            "Connection: keep-alive",
            "",
            body
        ]
        return "\r\n".join(response_lines).encode()

    def start(self):
        """Start the HTTP server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Serving on {self.host}:{self.port}")

        try:
            while True:
                # Accept new client connections
                client_socket, addr = server_socket.accept()
                print(f"Connection from {addr}")

                # Handle the client in a separate thread without immediate join
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()

        finally:
            server_socket.close()

if __name__ == "__main__":
    server = SimpleHTTPServer()
    server.start()
