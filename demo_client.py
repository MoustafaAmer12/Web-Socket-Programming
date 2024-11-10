from socket import *
import threading

serverName = "127.0.0.1"
serverPort = 8080

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

sentence = input("Input Lowercase setnence: ")
clientSocket.send(sentence.encode())

modifiedSentence = clientSocket.recv(1024)
print("From Server: ", modifiedSentence.decode())
clientSocket.close()