import socket
import threading
import os
import mimetypes
import uuid  # Import for generating unique filenames


class SimpleHTTPServer:
    def __init__(self, host='localhost', port=8081):
        self.host = host
        self.port = port
        self.timeout_idle = 10  
        self.timeout_busy = 5   
        self.connections = []   
        self.lock = threading.Lock()

    def handle_client(self, client_socket):
        with client_socket:
            with self.lock:
                self.connections.append(client_socket)

            print(f"Active connections: {len(self.connections)}")
            print(f"Clients: {self.connections}")
            print(f"Timeout: {self.get_dynamic_timeout()}")
            try:
                while True:
                    client_socket.settimeout(self.get_dynamic_timeout())
                    try:
                        request = client_socket.recv(1024)
                        if not request:
                            break

                        response = self.process_request(request, client_socket)
                        client_socket.sendall(response)

                        if b"Connection: close" in request:
                            break

                    except socket.timeout:
                        print("Connection timed out.")
                        break
                    except Exception as e:
                        print(f"Error: {e}")
                        break
            finally:
                with self.lock:
                    self.connections.remove(client_socket)

    def get_dynamic_timeout(self):
        """Adjust timeout based on server load."""
        with self.lock:
            num_connections = len(self.connections)
        return self.timeout_busy if num_connections > 5 else self.timeout_idle

    def process_request(self, request, client_socket):
        """Process a single HTTP request and return the response."""
        try:
            decoded_request = request.decode(errors='ignore')
            print("Received request:", decoded_request)
        except UnicodeDecodeError:
            print("Received non-UTF-8 request")
            return self.build_response(400, "Bad Request")

        lines = decoded_request.splitlines()
        if not lines:
            return self.build_response(400, "Bad Request")

        request_line = lines[0]
        method, path, _ = request_line.split()[:3]

        headers = {}
        for line in lines[1:]:
            if ": " in line:
                header, value = line.split(": ", 1)
                headers[header] = value

        if method == "GET":
            return self.handle_get(path)
        
        elif method == "POST":
            # Retrieve Content-Length and keep reading until full content is received
            content_length = int(headers.get("Content-Length", 0))
            body = b""
            while len(body) < content_length:
                chunk = client_socket.recv(min(4096, content_length - len(body)))
                if not chunk:  # Connection closed before full body was received
                    break
                body += chunk
            return self.handle_post(body)
        
        else:
            return self.build_response(405, "Method Not Allowed")

    def handle_get(self, path):
        """Handle GET requests by serving files or returning a 404."""
        if path == "/":
            path = "/index.html"

        filepath = "." + path
        if os.path.isfile(filepath):
            # Determine if the file should be read in binary mode
            mime_type, _ = mimetypes.guess_type(filepath)
            is_binary = mime_type and mime_type.startswith('image')
            
            # Read the file in binary or text mode based on its type
            mode = 'rb' if is_binary else 'r'
            with open(filepath, mode) as f:
                body = f.read()

            # Set the Content-Type header based on the file type
            content_type = mime_type if mime_type else 'application/octet-stream'
            return self.build_response(200, "OK", body, content_type)
        else:
            return self.build_response(404, "Not Found", "404 Not Found")

    def handle_post(self, body):
        """Handle POST requests by saving the received data to a file."""
        # Ensure the 'uploads' directory exists
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate a unique filename to prevent overwriting
        filename = f"{uuid.uuid4()}.dat"
        file_path = os.path.join(upload_dir, filename)
        
        # Write the received data to the file
        with open(file_path, 'wb') as f:
            f.write(body)
        
        print(f"POST data saved to {file_path}")

        # Respond with a success message
        response_body = f"File uploaded successfully as {filename}"
        return self.build_response(200, "OK", response_body)

    def build_response(self, status_code, status_text, body="", content_type="text/html"):
        """Construct an HTTP response based on the status code and body."""
        if isinstance(body, str):
            body = body.encode()  # Ensure the body is in bytes for binary compatibility

        response_lines = [
            f"HTTP/1.1 {status_code} {status_text}",
            f"Content-Type: {content_type}",
            f"Content-Length: {len(body)}",
            "Connection: keep-alive",
            "",
            ""
        ]
        return "\r\n".join(response_lines).encode() + body

    def start(self):
        """Start the HTTP server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(20)
        print(f"Serving on {self.host}:{self.port}")

        try:
            while True:
                client_socket, addr = server_socket.accept()
                print(f"Connection from {addr}")

                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()

        finally:
            server_socket.close()

if __name__ == "__main__":
    server = SimpleHTTPServer()
    server.start()
