import websockets
import asyncio
import json

clientsInQueue = []

ip = "100.66.219.46"
port = 1134

async def enterQueue(clientSocket):
    try:
        if len(clientsInQueue) > 0:
            otherClient = clientsInQueue.pop(0)
            matchResponse = {"response": "Match Found"}
            
            await clientSocket.send(json.dumps(matchResponse))
            await otherClient.send(json.dumps(matchResponse))
        else:
            clientsInQueue.append(clientSocket)
            waitingResponse = {"response": "Waiting for a match..."}
            await clientSocket.send(json.dumps(waitingResponse))

    except Exception as e:
        print(e)

async def newClientConnected(clientSocket, path):
    try:
        data = await clientSocket.recv()
        data = json.loads(data)

        if data["purpose"] == "enterQueue":
            await enterQueue(clientSocket)

    except websockets.ConnectionClosed:
        pass
    except Exception as e:
        print(e)
    finally:
        if clientSocket in clientsInQueue:
            clientsInQueue.remove(clientSocket)

async def startServer():
    print(f"Server started on {ip}:{port}")
    server = await websockets.serve(newClientConnected, ip, port)
    await server.wait_closed()

asyncio.run(startServer())