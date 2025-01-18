import websockets
import asyncio
import json

clientsInQueue = []

ip = "100.66.219.46"
port = 1134

async def enterQueue(clientSocket, data):
    try:
        if len(clientsInQueue) != 0:
            otherClient = clientsInQueue.pop(0)
            matchResponse = {"response": "Match Found"}
            
            await clientSocket.send(json.dumps(matchResponse))
            await otherClient.send(json.dumps(matchResponse))
        else:
            clientsInQueue.append(clientSocket)
            await clientSocket.send(json.dumps({"response": "Waiting for a match..."}))
            
            async for message in clientSocket:
                pass
    except Exception as e:
        print(f"Error in enterQueue: {e}")
    finally:
        if clientSocket in clientsInQueue:
            clientsInQueue.remove(clientSocket)


async def newClientConnected(clientSocket):
    try:
        data = await clientSocket.recv()
        data = json.loads(data)
        if data["purpose"] == "enterQueue":
            await enterQueue(clientSocket, data)
    except:
        pass


async def startServer():
    print(f"Server started on {ip}:{port}")
    await websockets.serve(newClientConnected, ip, port)

event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(startServer())
event_loop.run_forever()