import socket
import threading

HEADER = 64
PORT = 23
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "quit"
GROUP_ZERO = '00'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def write_log(msg):
    f = open("log.txt", "a")
    f.write(msg + "\r")
    f.close()


def formatting(msg):        # "0002 C1 01:13:02.877 00[CR]"
    data_tuple = tuple(msg.split())
    athlete, nn, time, group = data_tuple[0], data_tuple[1], data_tuple[2][:10], data_tuple[3][:2]
    if group == GROUP_ZERO:
        return f"athlete number {athlete} passed checkpoint {nn} at {time}"
    else:
        return ""


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr[0]} connected\r")

    connected = True
    while connected:
        msg = conn.recv(HEADER).decode(FORMAT)
        if msg == DISCONNECT_MESSAGE:
            connected = False
        else:
            write_log(msg)
            response = formatting(msg)
            if response.startswith("спортсмен"):
                print(response)
                conn.send(response.encode(FORMAT))

    conn.close()
    print("[DISCONNECTING] Connection is closed")


def start():
    server.listen()
    print(f"[LISTENING] Server is listening to {HOST}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
        conn.send(b"enter \"BBBB NN HH:MM:SS.zhq GG\" format to get result\r\n"
                  b"enter \"quit\" to leave\r\n")


if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start()
