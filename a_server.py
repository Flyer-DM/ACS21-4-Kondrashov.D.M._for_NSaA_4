import asyncio
import hashlib
import json
import datetime


async def logger(message: str) -> None:
    """Сохранение лог файла сервера"""
    with open('log.txt', 'a+') as f:  # лог файл
        f.write("{} | {}\n".format(str(datetime.datetime.now()), message))
    print(message)


async def send(writer: asyncio.StreamWriter, message: str) -> None:
    """Функция отправки сообщения клиенту"""
    writer.write(message.encode())
    await writer.drain()


async def enter_server(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Функция регистрации пользователя"""
    known = False
    await send(writer, "Welcome to async server! Let`s register! Enter your name, please: ")
    name = await reader.read(1024)
    await logger("Client connected.")
    if name.decode() != '':
        try:
            with open("clients.json", 'r') as clients_list:
                file_reader = json.load(clients_list)
                for elem in file_reader['clients']:
                    if elem['name'] == name.decode():
                       user_password, user_name, known = elem['password'], elem['name'], not known
                       await send(writer, f"Hello, {name.decode()}! Validate your password, please.")
                       break
        except json.JSONDecodeError:
           pass
        except FileNotFoundError:
            with open("clients.json", 'w') as clients_list:
                client_data = {'clients': []}
                json.dump(client_data, clients_list, indent=4)
        if known:  # подключение известного клиента
            await logger("Client is known.")
            attempts = 3  # три попытки на подтверждение пароля
            while True:
                password = await reader.read(1024)
                password = hashlib.md5(password).hexdigest()
                if attempts == 0:  # клиент не подтвердил свой пароль и был отключен от сервера
                    await send(writer, "Wrong password! Try again later.")
                    await logger("Client did not confirm his password and was disconnected.")
                    writer.close()
                    break
                if password == user_password:  # клиент подтвердил свой пароль
                    await send(writer, "You confirmed your password!")
                    await logger("Client confirmed his password.")
                    break
                else:  # клиент не подтвердил свой пароль, количество попыток уменьшено на одну
                    await send(writer, f"Wrong password! Try again, you have {attempts} attempts.")
                    attempts -= 1
        else:  # подключение нового клиента
            await logger("New client registration.")
            await send(writer, "You are new! Create password, please: ")
            password = await reader.read(1024)
            await send(writer, "Confirm your password, please: ")
            password_confirm = await reader.read(1024)
            if password == password_confirm:
                password = hashlib.md5(password).hexdigest()
                clients_list = open("clients.json", 'r')
                file_reader = json.load(clients_list)
                clients_list.close()
                file_reader['clients'].append({'password': password, 'name': name.decode()})
                with open("clients.json", 'w') as clients_list:
                    json.dump(file_reader, clients_list, indent=4)
                    await logger("New client ended his registration successfully.")
                    await send(writer, "Registration ended.")
            else:
                await send(writer, "You did not confirm your password and will be disconnected.")
                await logger("New client did not end his registration and was disconnected.")
                writer.close()


async def client_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Функция взаимодействия с пользователем после регистрации"""
    await enter_server(reader, writer)
    while True:
        incoming_message = (await reader.read(255)).decode()
        await logger("message: " + incoming_message)
        if incoming_message in ('exit', ''):
            break
        outcoming_message = incoming_message
        writer.write(outcoming_message.encode())
        try:
            await writer.drain()
        except ConnectionResetError:
            await logger("Client was disconnected because of some error.")
            break
    if incoming_message in ('exit', ''):
        await logger("Client was disconnected by his according to his desire.")
        writer.close()


async def run_server():
    """Основная функция запуска сервера"""
    server = await asyncio.start_server(client_handler, 'localhost', 1025)
    await logger(f"Server started his work at {server.sockets[0].getsockname()[1]}")
    async with server:
        await server.serve_forever()

try:
    asyncio.run(run_server())
except (KeyboardInterrupt, RuntimeError):
    with open('log.txt', 'a+') as f:
        f.write("{} | {}\n".format(str(datetime.datetime.now()), "Server closed."))
