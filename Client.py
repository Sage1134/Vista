import websockets
import asyncio
import json

socketAddress = "ws://100.66.219.46:1134"

async def toServer(purpose, data):
    data["purpose"] = purpose
    
    async with websockets.connect(socketAddress) as websocket:
        await websocket.send(json.dumps(data))

        response = await websocket.recv()
        response = json.loads(response)
        return response

async def main():
    testData = {}
    
    response = await toServer("enterQueue", testData)
    print(response["response"])

asyncio.run(main())