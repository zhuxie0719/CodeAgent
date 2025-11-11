import socket


def send():
    s = socket.socket()
    s.connect(("example.com", 80))
    s.send(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")
    # 未关闭套接字
    # socket_not_closed: medium



