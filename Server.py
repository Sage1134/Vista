from pymongo import MongoClient
from dotenv import load_dotenv
import asyncio
import json
import websockets
import os
import base64
from pathlib import Path
# from gen_ai.backend_ai import VideoMaker


def encode_image_to_base64(filepath):
    """
    Encodes an image file to a Base64 string.
    """
    file_path = Path(filepath)
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return encoded_string


def send_image_as_json(filepath):
    """
    Creates a JSON object containing the Base64-encoded image data.
    """
    try:
        encoded_image = encode_image_to_base64(filepath)
        image_json = {
            "filename": Path(filepath).name,
            "data": encoded_image
        }
        return json.dumps(image_json)
    except Exception as e:
        return json.dumps({"error": str(e)})


def encode_audio_to_base64(filepath):
    """
    Encodes an audio file to a Base64 string.
    """
    file_path = Path(filepath)
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return encoded_string


def send_audio_as_json(filepath):
    """
    Creates a JSON object containing the Base64-encoded audio data.
    """
    try:
        encoded_audio = encode_audio_to_base64(filepath)
        audio_json = {
            "filename": Path(filepath).name,
            "data": encoded_audio
        }
        return json.dumps(audio_json)
    except Exception as e:
        return json.dumps({"error": str(e)})


USER_STATE = {}
"""
USER_STATE[websocket] = {
    "status": "idle" or "waiting" or "matched",
    "question": str or None,
    "answer": str or None,
    "partner": websocket or None
}
"""

load_dotenv("vars.env")

uri = os.environ.get("MONGODB_URI")
ip = os.environ.get("BackendIP")
port = os.environ.get("Port")

mongoClient = MongoClient(uri)
database = mongoClient["Vista"]
collection = database["VistaCluster"]
usernames = {}


def getData(path):
    data = collection.find()

    for document in data:
        if document["_id"] == path[0]:
            data = document
            break
    else:
        return None

    for key in path:
        if key in data.keys():
            data = data[key]
        else:
            return None

    return data


def setData(path, data):
    newData = collection.find_one({"_id": path[0]})
    if newData != None:
        newData = dict(newData)
        dataUpdate = newData

        for key in enumerate(path):
            if key[0] != len(path) - 1:
                if key[1] in dataUpdate.keys():
                    if isinstance(dataUpdate[key[1]], dict):
                        dataUpdate = dataUpdate[key[1]]
                    else:
                        dataUpdate[key[1]] = {}
                        dataUpdate = dataUpdate[key[1]]
                else:
                    dataUpdate[key[1]] = {}
                    dataUpdate = dataUpdate[key[1]]
        dataUpdate[path[-1]] = data
        collection.find_one_and_replace({"_id": path[0]}, newData)

    else:
        newData = {}
        dataUpdate = newData

        for key in enumerate(path):
            dataUpdate[key[1]] = {}
            if (key[0] != len(path) - 1):
                dataUpdate = dataUpdate[key[1]]
        dataUpdate[path[-1]] = data

        newData["_id"] = path[0]
        collection.insert_one(newData)


def delData(path):
    data = collection.find()

    target = path.pop()

    for document in data:
        if len(path) != 0:
            if document["_id"] == path[0]:
                doc = document
                data = doc
                for key in path:
                    if key in data.keys():
                        data = data[key]
                if target in data.keys():
                    del data[target]

                collection.find_one_and_replace({"_id": path[0]}, doc)
                break
        else:
            collection.delete_one({"_id": target})


WAITING_QUEUE = []

ip = "LocalHost"
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

                yourPastPerspectives = getData(
                    ["pastPerspectives", usernames[client]])
                partnerPastPerspectives = getData(
                    ["pastPerspectives", usernames[partner]])

                if yourPastPerspectives == None:
                    yourPastPerspectives = []
                if partnerPastPerspectives == None:
                    partnerPastPerspectives = []

                yourRecentPerspective = [
                    USER_STATE[client["question"]], partner_answer]
                partnerRecentPerspective = [
                    USER_STATE[partner["question"]], your_answer]

                if len(yourPastPerspectives) < 5:
                    yourPastPerspectives.append(yourRecentPerspective)
                else:
                    yourPastPerspectives.pop(0)
                    yourPastPerspectives.append(yourRecentPerspective)

                if len(partnerPastPerspectives) < 5:
                    partnerPastPerspectives.append(partnerRecentPerspective)
                else:
                    partnerPastPerspectives.pop(0)
                    partnerPastPerspectives.append(partnerRecentPerspective)

                setData(["pastPerspectives", usernames[client]],
                        yourPastPerspectives)
                setData(["pastPerspectives", usernames[partner]],
                        partnerPastPerspectives)

                # yourPaths = VideoMaker().conv_resp_to_videos(
                #     USER_STATE[client]["question"], partner_answer, limit=1)
                # partnerPaths = VideoMaker().conv_resp_to_videos(
                #     USER_STATE[partner]["question"], your_answer, limit=1)

                # yourAudio = yourPaths.pop()
                # partnerAudio = partnerPaths.pop()

                # yourImage = send_image_as_json(f"./gen_ai/{yourPaths[0][2:]}")
                # partnerImage = send_image_as_json(
                #     f"./gen_ai/{partnerPaths[0][2:]}")

                # You are no longer recieving just a singular text answer on each socket. Instead, you are recieving in "photo" a single base 64 encoded image, and in "audio" a single base 64 encoded audio file.
                # await client.send(json.dumps({
                #     "response": "answerReceived",
                #     "photo": yourImage,
                #     "audio": send_audio_as_json(f"./gen_ai/{yourAudio[2:]}")
                # }))
                # await partner.send(json.dumps({
                #     "response": "answerReceived",
                #     "photo": partnerImage,
                #     "audio": send_audio_as_json(f"./gen_ai/{partnerAudio[2:]}")
                # }))

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
    elif mtype == "login":
        # When logging in OR signing up, set the "purpose" to "login" regardless of if they are signing up or registering. Also include a "username" field that is a string, saying what their username is.
        usernames[client] = msg.get("username")
    elif mtype == "getRecentPerspectives":
        # In order to get recent perspectives, simply send a message at any time with the purpose "getRecentPerspectives". See comment below to see how the response works.
        await client.send(json.dumps({
            "response": "recentPerspectives",
            "perspectives": getData(["pastPerspectives", usernames[client]])
        }))

        # list of UP TO 5 most recent perspectives, in the format [[question, answer], [question, answer], ...] in REVERSE ORDER. so first pair is longest ago perspective that is still stored.
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
