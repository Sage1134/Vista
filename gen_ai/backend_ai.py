import torch

# Verify GPU usage
print("Num GPUs Available: ", torch.cuda.device_count())
print("CUDA available: ", torch.cuda.is_available())

from damo_version import DAMO_MODEL
from openai import OpenAI
from os import getenv
from typing import List
from dotenv import load_dotenv, find_dotenv
import numpy as np
import os
from diffusers import AutoPipelineForText2Image

class VideoMaker:
    def __init__(self, fps=3, do_image=False):
        load_dotenv(find_dotenv())
        api_key = getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.messages = [
            {
                "role":"system",
                "content":"""An application involves anonymous queries and feedback or advice between two users. Person A will then receive the response in generative AI video format. """
            }
        ]

        if do_image:
            self.pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16")
            self.pipe.to("cuda")
        else:
            self.damo = DAMO_MODEL(fps=fps, level="med") # Used to be 10, then 5
        self.do_image = do_image 
        self.num_requests=0 # 0 if we overwrtite bread, 1 otherwise
        
    def make_images(self, name:str, steps:List[str]):
        try:
            os.mkdir(name)
        except:
            print("Directory already exists.")

        for i in range(len(steps)):
            picture_name = f"./{name}/picture{i+1}.png"

            prompt=steps[i]
            image = self.pipe(prompt=prompt, num_inference_steps=1, guidance_scale=0.0).images[0]
            print("Name", picture_name)
            image.save(picture_name)

    def conv_resp_to_videos(self, question:str, resp:str)->List[str]:
        """Given a user's response to a question, return the list of paths where the videos & audio can be found."""
        output_path = f"response-{self.num_requests}"

        # Audio Stuff
        # va = np.random.choice(['ash', 'onyx'], size=1)[0]
        with self.client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice='ash',
            input=resp
        ) as audio_response:
            audio_response.stream_to_file(os.path.join(output_path, "voice.mp3"))

        if self.do_image:
              # Image Stuff
            self.messages.append({
                "role":"user",
                "content":f"""Person A asked "{question}" and person B responded "{resp}". Create a prompt that can be fed into a generative AI that creates an image with accompanying audio in the format that you think would best deliver the feedback to Person A. Output only the prompt as raw text with no extra details whatsoever."""
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

            print("Prompt:", res)
            self.messages.pop()

            self.messages.append({
                "role":"user",
                "content":f"""Transform {res} into a list of subprompts/subscenes represented by a sentence.
                If there is no human in the scene, add one or more humans that are acting our the scene to the sentence.
                Remove all text in the scene and replace the text people acting out the text.
                Separate sentences by the newline character ("\n")."""
            })

            response2 = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.messages,
                temperature=1.0
            )

            if response2.choices:
                res2 = response2.choices[-1].message.content
            else:
                res2 = "Request 2 failed, for some reason."

            self.messages.pop()

            try:
                res2 = res2.split('\n')
                print(res2)

                # Make & store the images based on the number of requests we've had so far
                self.make_images(name=output_path, steps=res2)
                self.num_requests += 1
            except Exception as e:
                print(e)

        else:
            # Video Stuff
            self.messages.append({
                "role":"user",
                "content":f"""Person A asked "{question}" and person B responded "{resp}". Create a prompt that can be fed into a generative AI that creates a video with accompanying audio in the format that you think would best deliver the feedback to Person A. Output only the prompt as raw text with no extra details whatsoever."""
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

            print("Prompt:", res)
            self.messages.pop()

            self.messages.append({
                "role":"user",
                "content":f"""Transform {res} into a list of subprompts/subscenes represented by a sentence.
                If there is no human in the scene, add one or more humans that are acting our the scene to the sentence.
                Remove all text in the scene and replace the text people acting out the text.
                Separate sentences by the newline character ("\n")."""
            })

            response2 = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.messages,
                temperature=1.0
            )

            if response2.choices:
                res2 = response2.choices[-1].message.content
            else:
                res2 = "Request 2 failed, for some reason."

            self.messages.pop()

            try:
                res2 = res2.split('\n')
                print(res2)

                # Make & store the videos based on the number of requests we've had so far
                self.damo.make_videos(name=output_path, steps=res2)
                self.num_requests += 1
            except Exception as e:
                print(e)


if __name__ == "__main__":
    vmaker = VideoMaker(fps=3, do_image=True) # used to be 10 fps

    # ChatGPT decides what output format is best
        # e.g. Cooking bread -> Instructional video w/ audio
        #       Should I end contact w/ friend -> One-to-one chat w/ audio

    # bread just works ngl
    from bread_example import HOW_TO_BAKE_BREAD, HOW_QUESTION
    vmaker.conv_resp_to_videos(question=HOW_QUESTION, resp=HOW_TO_BAKE_BREAD)

    # Test for should I quit my job as well
        # Optimize for damo t2v 1.7b specifically
        # "Should I quit my job?" should be translated to "generate a video of someone quitting their job"
    from employment_example import HOW_TO_QUIT_JOB, HOW_QUESTION
    vmaker.conv_resp_to_videos(question=HOW_QUESTION, resp=HOW_TO_QUIT_JOB)