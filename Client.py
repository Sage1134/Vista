import asyncio
import websockets
import json

<<<<<<< HEAD
socketAddress = "ws://100.66.219.46:8080"
=======
socketAddress = "ws://100.66.219.46:1134"
>>>>>>> beda3aadd34c7192ef12115f70387197df2975d5


<<<<<<< HEAD
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
=======
    async def connect(self):
        """Connect to the server and start a background reader task."""
        self.websocket = await websockets.connect(socketAddress)
        print("Connected to server.")
        self.read_task = asyncio.create_task(self._read_messages())

    async def ask_question(self, question: str):
        """Send a question to be matched with another user."""
        if not self.websocket or self.websocket.closed:
            print("Not connected or already closed.")
            return
        msg = {"purpose": "askQuestion", "question": question}
        await self.websocket.send(json.dumps(msg))
        self.state = "waiting"

    async def provide_answer(self, answer: str):
        """Send an answer to your matched partner's question."""
        if not self.websocket or self.websocket.closed:
            print("Not connected or already closed.")
            return
        msg = {"purpose": "provideAnswer", "answer": answer}
        await self.websocket.send(json.dumps(msg))
        self.state = "waiting_for_partner"

    async def close(self):
        """Close the WebSocket connection and stop reading."""
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
        if self.read_task:
            self.read_task.cancel()

    async def _read_messages(self):
        """Continuously read and handle messages from the server."""
        try:
            async for raw_msg in self.websocket:
                try:
                    msg = json.loads(raw_msg)
                except json.JSONDecodeError:
                    print("[Error] Invalid JSON received:", raw_msg)
                    continue

                if msg.get("response") == "waiting":
                    print("Waiting for a match...")
                elif msg.get("response") == "matchFound":
                    their_question = msg["question"]
                    print(f"[Matched!] Partner's question: {their_question}")
                    self.state = "matched"
                elif msg.get("response") == "answerReceived":
                    print(f"[Answer received!] Your partner's advice: {msg['answer']}")
                    self.state = "idle"
                elif msg.get("response") == "partnerDisconnected":
                    print("[Notification] Your partner disconnected.")
                    self.state = "idle"
                elif msg.get("error"):
                    print(f"[Error] {msg['error']}")
>>>>>>> beda3aadd34c7192ef12115f70387197df2975d5
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
<<<<<<< HEAD
    asyncio.run(main())
=======
    asyncio.run(main())
>>>>>>> beda3aadd34c7192ef12115f70387197df2975d5
