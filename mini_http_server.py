# WebServer.py
from socket import *
import os

# server port and socket
serverPort = 6789
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# bind to all interfaces and start listening
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

print("web server running on port", serverPort)
print("waiting for connection...\n")

while True:
    # accept a single client connection
    connectionSocket, addr = serverSocket.accept()
    print("connected to client:", addr)

    try:
        # read raw http request
        data = connectionSocket.recv(2048).decode('iso-8859-1')
        if not data:
            connectionSocket.close()
            print("empty request, connection closed\n")
            continue

        # parse request line and method/path
        request_line = data.split("\r\n", 1)[0]
        parts = request_line.split()
        if len(parts) < 2 or parts[0] != "GET":
            # bad request for non-get or malformed line
            bad = "HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n"
            connectionSocket.send(bad.encode())
            connectionSocket.close()
            print("sent 400 bad request\n")
            continue

        # resolve requested path
        path = parts[1]
        if path == "/":
            path = "/HelloWorld.html"
        filename = path.lstrip("/")

        with open(filename, "rb") as f:
            body = f.read()

        # simple content-type detection
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        mime = {
            "html": "text/html",
            "htm": "text/html",
            "css": "text/css",
            "js": "application/javascript",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "txt": "text/plain"
        }.get(ext, "application/octet-stream")

        # send success headers and body
        headers = [
            "HTTP/1.1 200 OK",
            f"Content-Type: {mime}",
            f"Content-Length: {len(body)}",
            "Connection: close",
            "\r\n"
        ]
        connectionSocket.send("\r\n".join(headers).encode())
        connectionSocket.sendall(body)
        print("file sent:", filename, "\n")

    except FileNotFoundError:
        # send not found response
        body = b"<html><body><h1>404 not found</h1></body></html>"
        headers = [
            "HTTP/1.1 404 Not Found",
            "Content-Type: text/html",
            f"Content-Length: {len(body)}",
            "Connection: close",
            "\r\n"
        ]
        connectionSocket.send("\r\n".join(headers).encode())
        connectionSocket.sendall(body)
        print("file not found, sent 404\n")

    except Exception as e:
        try:
            response = "HTTP/1.1 500 Internal Server Error\r\nConnection: close\r\n\r\n"
            connectionSocket.send(response.encode())
        except:
            pass
        print("internal error:", e, "\n")

    finally:
        connectionSocket.close()        # close connection after serving one request
        print("connection closed\n")
