import asyncio
import json
import websockets

socketAddress = "ws://100.66.219.46:1134"

class QuestionClient:
    def __init__(self):
        self.websocket = None
        self.read_task = None
        self.state = "idle"  # Possible states: idle, waiting, matched, waiting_for_partner
        self.previous_state = None

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
                else:
                    print("[Server message]", msg)
        except asyncio.CancelledError:
            pass
        except websockets.ConnectionClosed:
            print("Connection closed by server.")
        except Exception as e:
            print("Error in read loop:", e)

async def main():
    client = QuestionClient()
    await client.connect()

    try:
        while True:
            if client.state != client.previous_state:
                if client.state == "idle":
                    question = input("Enter your question: ").strip()
                    await client.ask_question(question)
                elif client.state == "matched":
                    answer = input("Enter your answer: ").strip()
                    await client.provide_answer(answer)
                elif client.state == "waiting_for_partner":
                    print("Waiting for your partner to answer...")
                client.previous_state = client.state
            await asyncio.sleep(0.1)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())