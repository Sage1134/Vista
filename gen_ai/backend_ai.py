import torch

# Verify GPU usage
print("Num GPUs Available: ", torch.cuda.device_count())
print("CUDA available: ", torch.cuda.is_available())

from damo_version import DAMO_MODEL
from openai import OpenAI
from os import getenv
from typing import List
from dotenv import load_dotenv, find_dotenv

class VideoMaker:
    def __init__(self, fps=3):
        load_dotenv(find_dotenv())
        api_key = getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.messages = [
            {
                "role":"system",
                "content":"""Transform the following string into a list of sentences representing the same process to optimize performance of damo-vilab/text-to-video-ms-1.7b, a text-to-video model. 
                Each sentence should contain 1 verb. If a sentence does not have a verb, remove it. Separate sentences by the newline character ("\n")."""
            }
        ]

        self.damo = DAMO_MODEL(fps=fps) # Used to be 10, then 5
        self.num_requests=0
        
    def conv_resp_to_videos(self, resp:str)->List[str]:
        """Given a user's response to a question, return the list of paths where the videos can be found."""

        self.messages.append({
            "role":"user",
            "content":resp
        })

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages,
            temperature=1.0
        )

        if response.choices:
            res = response.choices[-1].message.content
        else:
            res = "Request failed (for some unknown reason)."

        try:
            res = res.split('\n')
            print(res)

            # Make & store the videos based on the number of requests we've had so far
            self.damo.make_videos(name=f"response-{self.num_requests}", steps=res)
            self.num_requests += 1
        except Exception as e:
            print(e)


if __name__ == "__main__":
    vmaker = VideoMaker(fps=3)

    # ChatGPT decides what output format is best
        # e.g. Cooking bread -> Instructional video w/ audio
        #       Should I end contact w/ friend -> One-to-one chat w/ audio

    from bread_example import HOW_TO_BAKE_BREAD
    vmaker.conv_resp_to_videos(resp=HOW_TO_BAKE_BREAD)

    # Test for should I quit my job as well
        # Optimize for damo t2v 1.7b specifically
        # "Should I quit my job?" should be translated to "generate a video of someone quitting their job"
    from employment_example import HOW_TO_QUIT_JOB
    vmaker.conv_resp_to_videos(resp=HOW_TO_QUIT_JOB)