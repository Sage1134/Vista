import websockets
import asyncio
import json

socketAddress = "ws://100.66.219.46:1134"

async def toServer(purpose, data):
    data["purpose"] = purpose
    
    try:
        async with websockets.connect(socketAddress) as websocket:
            await websocket.send(json.dumps(data))
            
            while True:
                response = await websocket.recv()
                response = json.loads(response)
                print(response["response"])
                
                if response["response"] == "Match Found":
                    break
    except Exception as e:
        print(e)

async def main():
    testData = {}
    await toServer("enterQueue", testData)

asyncio.run(main())