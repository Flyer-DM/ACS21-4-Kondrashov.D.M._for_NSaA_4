import asyncio


async def client_handle(reader, writer):
    incoming_message: str = ''
    while incoming_message != 'exit':
        incoming_message = (await reader.read(255)).decode()
        outcoming_message = incoming_message
        writer.write(outcoming_message.encode())
        await writer.drain()
    writer.close()


async def run_server():
    server = await asyncio.start_server(client_handle, 'localhost', 1025)
    async with server:
        await server.serve_forever()


asyncio.run(run_server())
