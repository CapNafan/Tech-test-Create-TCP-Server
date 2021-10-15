import socket
import threading
import re

HEADER = 64
PORT = 8080
HOST = "127.0.0.1"
ADDR = (HOST, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "quit"
GROUP_ZERO = '00'


def write_log(msg):
    f = open("log.txt", "a")
    f.write(msg + "\r")
    f.close()


def validate(msg):
    return re.match(r"\d{4}\s*[A-Z]\d\s*\d{2}[:]\d{2}[:]\d{2}[.]\d{3}\s*\d{2}", msg)


def process_message(msg):        # "0002 C1 01:13:02.877 00[CR]"
    if not validate(msg):
        raise ValueError
    data_tuple = tuple(msg.split())
    athlete, nn, time, group = data_tuple[0], data_tuple[1], data_tuple[2][:10], data_tuple[3][:2]
    if group == GROUP_ZERO:
        return True, f"спортсмен, нагрудный номер {athlete} прошёл отсечку {nn} в {time}\n\r"
    else:
        return False, msg


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr[0]} connected\r")

    connected = True
    while connected:
        msg = conn.recv(HEADER).decode(FORMAT)
        if msg == DISCONNECT_MESSAGE:
            connected = False
        else:
            try:
                is_processed, response = process_message(msg)
                if is_processed:
                    print(response[:-4])
                    conn.send(response.encode(FORMAT))
                write_log(msg)
            except ValueError:
                conn.send(b" Wrong data format!\r\n")

    conn.close()
    print("[DISCONNECTING] Connection is closed")


def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening to {HOST} on port {PORT}")

    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
    conn.send(b"enter \"BBBB NN HH:MM:SS.zhq GG\" format to get result\r\n"
              b"enter \"quit\" to leave\r\n")


if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start()
