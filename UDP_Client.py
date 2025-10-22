from socket import *
import time

serverName = '127.0.0.1'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

message = input("Input lowercase sentence: ")
start = time.time()
clientSocket.sendto(message.encode(), (serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
end = time.time()

print(modifiedMessage.decode())
print("Message sent to server:", message)
print("Starting time: ", start * 1000, "ms")
print("Ending time: ", end * 1000, "ms")
print("RTT: ", (end - start) * 1000, "ms")

clientSocket.close()
