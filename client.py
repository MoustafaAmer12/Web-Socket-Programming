import socket
import sys
import os

DEFAULT_PORT = 8081
DEFAULT_HOST = "localhost"

def create_request(command_type, file_path, host_name):
    if command_type == "client_get":
        return f"GET /{file_path} HTTP/1.1\r\nHost: {host_name}\r\nConnection: close\r\n\r\n"
    elif command_type == "client_post":
        body = "name=example&value=test"
        return f"POST /{file_path} HTTP/1.1\r\nHost: {host_name}\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}"
    return ""

def parse_command(line):
    parts = line.strip().split()
    command_type = parts[0]
    file_path = parts[1]
    host_name = DEFAULT_HOST
    port = DEFAULT_PORT
    return command_type, file_path, host_name, port

def save_response(file_path, response_body):
    # Ensure the 'output' directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct the full path for saving the file in the output directory
    full_path = os.path.join(output_dir, os.path.basename(file_path))
    
    # Save the response body to the specified file path
    with open(full_path, 'wb') as f:
        f.write(response_body)

def handle_response(command_type, file_path, response):
    headers, _, body = response.partition(b"\r\n\r\n")
    print("Headers:\n", headers.decode())
    if command_type == "client_get":
        save_response(file_path, body)
        print(f"File '{file_path}' saved.")

def execute_command(command_type, file_path, host_name, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host_name, port))
        request = create_request(command_type, file_path, host_name)
        s.sendall(request.encode())
        
        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
        
        handle_response(command_type, file_path, response)

def run_client(input_file):
    with open(input_file, 'r') as f:
        for line in f:
            if line.strip():
                command_type, file_path, host_name, port = parse_command(line)
                execute_command(command_type, file_path, host_name, port)

if __name__ == "__main__":
    # Run with: python3 my_client.py input.txt
    if len(sys.argv) != 2:
        print("Usage: python3 my_client.py <input_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    run_client(input_file)
