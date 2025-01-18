# pip install diffusers transformers accelerate opencv-python
# pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

import time
import torch
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.utils import export_to_video
from typing import List

# example user inputs, from asker and receiver
from bread_example import BREAD_STEPS, HOW_QUESTION, HOW_TO_BAKE_BREAD, BAD_BREAD_STEPS

class DAMO_MODEL:
    def __init__(self):
        print("Loading model...")
        start = time.time()
        self.pipe = DiffusionPipeline.from_pretrained("damo-vilab/text-to-video-ms-1.7b", torch_dtype=torch.float16, variant="fp16")
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.enable_model_cpu_offload()

        end = time.time()
        print(f"Model loaded in {(end - start):.2f} seconds!")

    def make_videos(self, name:str, steps:List[str]) -> None:
        for i in range(len(steps)):
            prompt=steps[i]

            # get first video in batch
            # started as 25 inference steps
            video_frames = self.pipe(prompt, num_inference_steps=125).frames[0] 
            video_path = export_to_video(video_frames, fps=10, output_video_path=f"{name}-step-{i+1}.mp4")
            video_name = video_path
            print("Name", video_name)
            torch.cuda.empty_cache()

if __name__ == "__main__":
    damo = DAMO_MODEL()
    damo.make_videos(name="BREAD", steps=BREAD_STEPS)
    damo.make_videos(name="BAD BREAD", steps=BAD_BREAD_STEPS)