import asyncio


HOST = 'localhost'
PORT = 1025


async def server_handle(host, port):
    outcoming_message = ''
    try:
        reader, writer = await asyncio.open_connection(host, port)
        incoming_message = await reader.read(255)
        print('message:', incoming_message.decode())
        while outcoming_message != 'exit':
            outcoming_message = input('you: ')
            writer.write(outcoming_message.encode())
            await writer.drain()
            incoming_message = await reader.read(255)
            print('message:', incoming_message.decode())
            if incoming_message.decode() in ("You didn`t confirm your password and will be disconnected.",
                                             "Wrong password! Try again later."):
                break
        print("Disconnected from server.")
        writer.close()
        await writer.wait_closed()
    except ConnectionRefusedError:
        print("Connection impossible.")
    except (ConnectionAbortedError, ConnectionResetError):
        print("You was disconnected from server.")

asyncio.run(server_handle(HOST, PORT))
