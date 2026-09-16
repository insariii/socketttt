import socket
import threading

from protocol import send_message, recv_message


HOST = '127.0.0.1'
PORT = 8080


def receive_messages(s):
    try:
        while True:
            message = recv_message(s)

            if message is None:
                print("Сервер закрыл соединение")
                break

            command, data = message

            text = data.decode("utf-8")

            if command == "TEXT":
                print(f"{text}")

            elif command == "LIST":
                print("Пользователи:")
                print(text)

            elif command == "ERR!":
                print(f"Ошибка: {text}")

    except ConnectionResetError:
        print("Соединение сброшено")

    except ConnectionError:
        print("Соединение закрыто")

    except BrokenPipeError:
        print("Соединение разорвано")

    except OSError as error:
        print(f"Ошибка: {error}")


username = input("Введите имя: ")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect((HOST, PORT))

    print("Подключились к серверу")

    send_message(
        s,
        "JOIN",
        username.encode("utf-8")
    )

    thread = threading.Thread(
        target=receive_messages,
        args=(s,),
        daemon=True
    )

    thread.start()

    print()
    print("Команды:")
    print("/list - список пользователей")
    print("/quit - выйти")
    print()

    while True:
        text = input("> ")

        if text == "/list":
            send_message(
                s,
                "LIST",
                b""
            )

        elif text == "/quit":
            send_message(
                s,
                "QUIT",
                b""
            )
            break

        elif text:
            send_message(
                s,
                "TEXT",
                text.encode("utf-8")
            )

except ConnectionRefusedError:
    print("Сервер недоступен")

except ConnectionResetError:
    print("Соединение сброшено")

except BrokenPipeError:
    print("Соединение разорвано")

except OSError as error:
    print(f"Ошибка: {error}")

finally:
    s.close()
