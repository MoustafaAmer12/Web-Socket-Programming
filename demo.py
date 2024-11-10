from socket import *

serverPort = 8080
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('127.0.0.1', serverPort))

serverSocket.listen(1)
print('The server is ready to receive')

while True:
    connectionScocket, addr = serverSocket.accept()
    sentence = connectionScocket.recv(1024).decode()
    capitalizedSentence = sentence.upper()
    connectionScocket.send(capitalizedSentence.encode())
    connectionScocket.close()