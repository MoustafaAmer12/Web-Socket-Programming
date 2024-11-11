import socket
import os
import webbrowser
import io
from PIL import Image
import subprocess

# Function to send GET request to the server
def send_get_request(client_socket, path):
    request = (f"GET /{path} HTTP/1.1\r\n"
                "Host: 127.0.0.1\r\n"
               f"Client-ID: {0}\r\n"
               f"Connection: keep-alive\r\n\r\n")
    client_socket.sendall(request.encode('utf-8'))


# Main client function
def test_client():
    # Connect to the server
    server_ip = '127.0.0.1'
    server_port = 8080
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    # Test GET requests for image, text, and HTML files
    print("Sending GET request for an image...")
    send_get_request(client_socket, "pages/dummy.png")
    response = client_socket.recv(4096)
    print(f"Received response for image:\n{response}\n")
    with open("temp_image.jpg", "wb") as f:
        f.write(response)
    # Use feh to open the image
    subprocess.run(["feh", "temp_image.jpg"])

    print("Sending GET request for a text file...")
    send_get_request(client_socket, "get_test.txt")
    response = client_socket.recv(4096)
    print(f"Received response for text file:\n{response.decode('utf-8')}\n")

    print("Sending GET request for an HTML file...")
    send_get_request(client_socket, "pages/crc.html")
    response = client_socket.recv(4096)
    with open("temp_page.html", "w") as file:
        file.write(response.decode('utf-8'))
    webbrowser.open("file://" + os.path.realpath("temp_page.html"))
    print(f"Received response for HTML file:\n{response[:50]}\n")

    # Close the connection
    client_socket.close()

if __name__ == "__main__":
    test_client()
