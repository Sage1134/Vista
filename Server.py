import websockets
import asyncio
import json

connectedClients = set()

ip = "100.66.219.46"
port = 1134

async def testing(client_socket, data):
    try:
        data = {"response": data["test"] + "Test"}
        await client_socket.send(json.dumps(data))
    except:
        pass
    finally:
        connectedClients.remove(client_socket)

async def newClientConnected(client_socket):
    try:
        connectedClients.add(client_socket)
        data = await client_socket.recv()
        data = json.loads(data)
        if data["purpose"] == "testing":
            await testing(client_socket, data)
    except:
        pass


async def startServer():
    print(f"Server started on {ip}:{port}")
    await websockets.serve(newClientConnected, ip, port)

event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(startServer())
event_loop.run_forever()