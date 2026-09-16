import socket
import struct


MAX_MESSAGE_SIZE = 10 * 1024 * 1024


def recv_exact(sock, size):
    data = bytearray()

    while len(data) < size:
        part = sock.recv(size - len(data))

        if not part:
            raise ConnectionError("Соединение закрыто")

        data.extend(part)

    return bytes(data)


def send_message(sock, command, payload):
    command = command.encode("utf-8")

    if len(command) != 4:
        raise ValueError("Команда должна занимать 4 байта")

    if len(payload) > MAX_MESSAGE_SIZE:
        raise ValueError("Сообщение слишком большое")

    header = command + struct.pack("!I", len(payload))

    sock.sendall(header)
    sock.sendall(payload)


def recv_message(sock):
    header = sock.recv(8)

    if not header:
        return None

    if len(header) < 8:
        header += recv_exact(sock, 8 - len(header))

    command = header[:4].decode("utf-8")
    size = struct.unpack("!I", header[4:8])[0]

    if size > MAX_MESSAGE_SIZE:
        raise ValueError("Сообщение слишком большое")

    data = recv_exact(sock, size)

    return command, data
