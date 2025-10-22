"""
Mini HTTP Server — handles ONE request at a time (sequentially).
- Accepts and parses a basic HTTP GET request.
- Serves a file from the current directory with HTTP/1.1 headers.
- Returns 404 Not Found if the file doesn't exist.
"""

from socket import *
import os
import datetime

HOST = ""          # Listen on all interfaces
PORT = 6789        # Change if needed; must match the URL you test with
BUF_SIZE = 4096

def http_date_now():
    """Return current time formatted per RFC 1123 (GMT)."""
    return datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

def guess_type(path):
    """Very small content-type mapper; good enough for the lab."""
    path = path.lower()
    if path.endswith('.html') or path.endswith('.htm'):
        return 'text/html; charset=utf-8'
    if path.endswith('.txt'):
        return 'text/plain; charset=utf-8'
    if path.endswith('.css'):
        return 'text/css; charset=utf-8'
    if path.endswith('.js'):
        return 'application/javascript'
    if path.endswith('.png'):
        return 'image/png'
    if path.endswith('.jpg') or path.endswith('.jpeg'):
        return 'image/jpeg'
    return 'application/octet-stream'

def build_response(status_code, body=b'', content_type='text/html; charset=utf-8'):
    """Build a raw HTTP/1.1 response with minimal headers."""
    reason = {200: 'OK', 404: 'Not Found', 400: 'Bad Request', 405: 'Method Not Allowed'}.get(status_code, 'OK')
    headers = [
        f'HTTP/1.1 {status_code} {reason}',
        f'Date: {http_date_now()}',
        'Server: MiniPythonServer/0.1',
        f'Content-Length: {len(body)}',
        'Connection: close'
    ]
    if status_code == 200:
        headers.append(f'Content-Type: {content_type}')
    head = '\r\n'.join(headers).encode('utf-8') + b'\r\n\r\n'
    return head + body

def serve_once(conn):
    """Handle exactly one HTTP request on a connected socket."""
    request = b''
    # Read until end of headers or client closes
    while b'\r\n\r\n' not in request:
        chunk = conn.recv(BUF_SIZE)
        if not chunk:
            break
        request += chunk

    if not request:
        return

    # Minimal parse: first line like "GET /path HTTP/1.1"
    try:
        first_line = request.split(b'\r\n', 1)[0].decode('iso-8859-1')
        method, target, _version = first_line.split(' ', 2)
    except Exception:
        conn.sendall(build_response(400, b'Bad Request'))
        return

    if method != 'GET':
        conn.sendall(build_response(405, b'Only GET supported'))
        return

    # Map "/" -> default file
    if target == '/':
        target = '/HelloWorld.html'

    # Normalize path and prevent "../" traversal
    safe_path = os.path.normpath(target.lstrip('/'))
    if safe_path.startswith('..'):
        conn.sendall(build_response(404, b'Not Found'))
        return

    if os.path.isfile(safe_path):
        with open(safe_path, 'rb') as f:
            body = f.read()
        conn.sendall(build_response(200, body, content_type=guess_type(safe_path)))
    else:
        body = b'<h1>404 Not Found</h1>'
        conn.sendall(build_response(404, body))

def main():
    with socket(AF_INET, SOCK_STREAM) as srv:
        srv.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(1)
        print(f'[+] Server listening on 0.0.0.0:{PORT} (one request at a time)')
        while True:
            conn, addr = srv.accept()
            print(f'[+] Client connected from {addr[0]}:{addr[1]}')
            with conn:
                serve_once(conn)
            print('[*] Request handled, connection closed. Ready for the next one...')

if __name__ == '__main__':
    main()
