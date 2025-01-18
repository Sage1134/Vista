from lumaai import LumaAI
from dotenv import load_dotenv
from os import getenv
import requests
import time

# example user inputs, from asker and receiver
from bread_example import BREAD_STEPS, HOW_QUESTION, HOW_TO_BAKE_BREAD

print("Are you sure you want to run? You must run the whole file WITHOUT STOP, or you will be wasting a LOT of money.")
user_input = input("Proceed? (Y/N) ")

if user_input != "Y":
    raise RuntimeError("User chose to stop.")

load_dotenv()
LUMA_API_KEY = getenv('LUMA_KEY')

client = LumaAI(
    auth_token=LUMA_API_KEY
)

for i in range(len(BREAD_STEPS)):

    # for more complex processes, we should divide them into procedures and feed them, one at a time.
    generation = client.generations.create(
        # prompt=HOW_TO_BAKE_BREAD, 
        # prompt=HOW_QUESTION, 
        prompt=BREAD_STEPS[i], 
        aspect_ratio="1:1", 
        loop=False
    )


    start = time.time()
    completed = False
    while not completed:
        generation = client.generations.get(id=generation.id, resolution="144p")
        if generation.state == 'completed':
            end = time.time()
            completed = True
        elif generation.state == 'failed':
            end = time.time()
            raise RuntimeError(f"Generation failed: {generation.failure_reason}")
        print(f"Generating video-{i}...")
        time.sleep(3)
        
    video_url = generation.assets.video
        
    # get the video, once its done
    response = requests.get(video_url, stream=True)
    with open(f'./videos/step-{i}.mp4', 'wb') as file:
        file.write(response.content)
    print(f"File downloaded as ./videos/step-{i}.mp4") # - $0.40 per run lol
    print(f"Took {end - start} seconds to generate that.")
    
print(f"Your videos are done generating. That cost ${0.4*len(BREAD_STEPS):.2f}.")