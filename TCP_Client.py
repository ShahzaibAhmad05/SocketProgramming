from socket import *
import time

serverName = '127.0.0.1'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)

start_time = time.time()
clientSocket.connect((serverName, serverPort))

message = input("Input lowercase sentence: ")
start = time.time()
clientSocket.send(message.encode())
modifiedSentence = clientSocket.recv(1024)
end_time = time.time()

print(modifiedSentence.decode())
print("Message sent to server:", message)
print("Connection request time:", start_time * 1000, " ms")
print("Reply received time:", end_time, " ms")
print("RTT:", (end_time - start_time) * 1000, " ms")

clientSocket.close()
