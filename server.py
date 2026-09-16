import socket
import threading

from protocol import send_message, recv_message


HOST = '0.0.0.0'
PORT = 8080

clients = {}


def client_thread(conn, addr):
    username = None

    try:
        while True:
            message = recv_message(conn)

            if message is None:
                break

            command, data = message

            if command == "JOIN":
                username = data.decode("utf-8")

                clients[conn] = username

                print(f"Подключился клиент: {addr}")
                print(f"Имя пользователя: {username}")

            elif command == "TEXT":
                text = data.decode("utf-8")

                print(f"{username}: {text}")

                for client in list(clients):
                    if client != conn:
                        try:
                            send_message(
                                client,
                                "TEXT",
                                f"{username}: {text}".encode("utf-8")
                            )
                        except (ConnectionResetError, BrokenPipeError, OSError):
                            pass

            elif command == "LIST":
                users = "\n".join(clients.values())

                send_message(
                    conn,
                    "LIST",
                    users.encode("utf-8")
                )

            elif command == "QUIT":
                print(f"{username} вышел из чата")
                break

            else:
                send_message(
                    conn,
                    "ERR!",
                    f"Неизвестная команда: {command}".encode("utf-8")
                )

    except ConnectionResetError:
        print(f"Соединение сброшено: {addr}")

    except ConnectionError:
        print(f"Соединение закрыто: {addr}")

    except BrokenPipeError:
        print(f"Соединение разорвано: {addr}")

    except OSError as error:
        print(f"Ошибка: {error}")

    finally:
        clients.pop(conn, None)

        conn.close()

        if username:
            for client in list(clients):
                try:
                    send_message(
                        client,
                        "TEXT",
                        f"Система: {username} вышел из чата".encode("utf-8")
                    )
                except (ConnectionResetError, BrokenPipeError, OSError):
                    pass

        print(f"Клиент отключился: {addr}")


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((HOST, PORT))
s.listen()

print("Сервер слушает...")


try:
    while True:
        conn, addr = s.accept()

        print(f"Подключился клиент: {addr}")

        thread = threading.Thread(
            target=client_thread,
            args=(conn, addr)
        )

        thread.start()

except KeyboardInterrupt:
    print("Сервер остановлен")

finally:
    s.close()
