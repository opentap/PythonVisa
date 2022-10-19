# Based on https://stackoverflow.com/questions/54408940/how-to-write-a-python-echo-server-that-doesnt-disconnect-after-first-echo
# server.py:
import socket

HOST = '127.0.0.1' 
PORT = 5025

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        while True:
            data = conn.recv(1024)
            if data.decode() == "bye":
                break
            conn.sendall(data)
            conn, addr = s.accept()
