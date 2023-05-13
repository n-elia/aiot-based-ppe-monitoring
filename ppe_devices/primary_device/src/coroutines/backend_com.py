import uasyncio
from primitives.queue import Queue


async def backend_communication_coro(hostname: str, port: int, outgoing_messages_queue: Queue, enabled=True):
    '''
    This coroutine processes the queue of messages to be sent to the backend server.
    '''
    if not enabled:
        return

    import usocket as socket

    sock = socket.socket()

    def close_socket():
        sock.close()
        print('backend_communication_coro: server disconnected.')

    try:
        server = socket.getaddrinfo(hostname, port)[0][-1]
        sock.connect(server)

    except OSError as e:
        print('backend_communication_coro: cannot connect to {} on port {}'.format(
            hostname, port))
        sock.close()
        return

    swriter = uasyncio.StreamWriter(sock, {})

    while True:
        msg = await outgoing_messages_queue.get()
        print(
            f"backend_communication_coro: sending message {msg} to {hostname}:{port}")

        try:
            swriter.write(msg)
            await swriter.drain()

        except OSError:
            close_socket()
            return
