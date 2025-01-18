import asyncio
import json
import websockets

USER_STATE = {}
"""
USER_STATE[websocket] = {
    "status": "idle" or "waiting" or "matched",
    "question": str or None,
    "answer": str or None,
    "partner": websocket or None
}
"""

WAITING_QUEUE = []

ip = "100.66.219.46"
port = 1134

async def match_two_clients(client_a, client_b):
    USER_STATE[client_a]["status"] = "matched"
    USER_STATE[client_b]["status"] = "matched"

    await client_a.send(json.dumps({
        "response": "matchFound",
        "question": USER_STATE[client_b]["question"]
    }))
    await client_b.send(json.dumps({
        "response": "matchFound",
        "question": USER_STATE[client_a]["question"]
    }))

    USER_STATE[client_a]["partner"] = client_b
    USER_STATE[client_b]["partner"] = client_a

async def process_message(client, msg):
    mtype = msg.get("purpose")

    if mtype == "askQuestion":
        if USER_STATE[client]["status"] == "idle":
            question = msg.get("question", "")
            USER_STATE[client]["question"] = question
            USER_STATE[client]["status"] = "waiting"

            if WAITING_QUEUE:
                other = WAITING_QUEUE.pop(0)
                await match_two_clients(client, other)
            else:
                WAITING_QUEUE.append(client)
                await client.send(json.dumps({"response": "waiting"}))
        else:
            print("Client is not idle, ignoring question")

    elif mtype == "provideAnswer":
        if USER_STATE[client]["status"] == "matched":
            USER_STATE[client]["answer"] = msg.get("answer", "")
            partner = USER_STATE[client].get("partner")

            if partner and USER_STATE[partner].get("answer") is not None:
                your_answer = USER_STATE[client]["answer"]
                partner_answer = USER_STATE[partner]["answer"]

                await client.send(json.dumps({
                    "response": "answerReceived",
                    "answer": partner_answer
                }))
                await partner.send(json.dumps({
                    "response": "answerReceived",
                    "answer": your_answer
                }))

                USER_STATE[client].update({
                    "status": "idle",
                    "question": None,
                    "answer": None,
                    "partner": None
                })
                USER_STATE[partner].update({
                    "status": "idle",
                    "question": None,
                    "answer": None,
                    "partner": None
                })
        else:
            print("Client is not matched, ignoring answer")
    else:
        print("Unknown Message")

async def client_handler(client):
    USER_STATE[client] = {
        "status": "idle",
        "question": None,
        "answer": None,
        "partner": None
    }

    try:
        async for raw_msg in client:
            try:
                msg = json.loads(raw_msg)
            except:
                await client.send(json.dumps({"error": "Invalid JSON"}))
                continue

            await process_message(client, msg)

    except websockets.ConnectionClosed:
        pass
    finally:
        if client in WAITING_QUEUE:
            WAITING_QUEUE.remove(client)

        partner = USER_STATE[client].get("partner")
        if partner:
            USER_STATE[partner]["partner"] = None
            USER_STATE[partner]["answer"] = None
            if USER_STATE[partner]["status"] == "matched":
                await partner.send(json.dumps({"response": "partnerDisconnected"}))
                USER_STATE[partner]["status"] = "idle"

        USER_STATE.pop(client, None)
        await client.close()

async def main():
    print(f"Server listening on {ip}:{port}")
    server = await websockets.serve(client_handler, ip, port)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())