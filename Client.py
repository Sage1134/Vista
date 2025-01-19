import asyncio
import websockets
import json

socketAddress = "ws://100.66.219.46:8080"


async def handle_client(websocket, path):
    async for message in websocket:
        try:
            msg = json.loads(message)
            if msg["purpose"] == "signIn":
                username = msg["username"]
                password = msg["password"]
                # Handle the login logic here
                if username == "correctUsername" and password == "correctPassword":  # Example check
                    response = {"response": "signInSuccess",
                                "username": username, "sessionID": "dummySessionID"}
                else:
                    response = {"response": "fail"}
                await websocket.send(json.dumps(response))
        except Exception as e:
            print(f"Error handling message: {e}")


async def main():
    server = await websockets.serve(handle_client, "0.0.0.0", 8080)
    print("Server started on ws://0.0.0.0:8080")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
