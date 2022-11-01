import asyncio


HOST = 'localhost'
PORT = 1025


async def server_handle(host, port):
    outcoming_message = ''
    try:
        reader, writer = await asyncio.open_connection(host, port)
        while outcoming_message != 'exit':
            outcoming_message = input('you: ')
            writer.write(outcoming_message.encode())
            await writer.drain()
            incoming_message = await reader.read(255)
            print('message:', incoming_message.decode())
        print('disconnected from server.')
        writer.close()
        await writer.wait_closed()
    except ConnectionRefusedError:
        print("Connection impossible.")


asyncio.run(server_handle(HOST, PORT))
