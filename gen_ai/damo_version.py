import time
import torch
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from typing import List
import os

class DAMO_MODEL:
    def __init__(self, fps, level="high"):
        print("Loading model...")
        start = time.time()
        self.pipe = DiffusionPipeline.from_pretrained("damo-vilab/text-to-video-ms-1.7b", torch_dtype=torch.float16, variant="fp16")

        if level == "high":
            self.quality = 10
        elif level == "med":
            self.quality = 4 # 5 used to work
        else:
            self.quality = 1
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
        
        # Offload model to CPU when not in use
        self.pipe.enable_model_cpu_offload()

        self.fps = fps

        end = time.time()
        print(f"Model loaded in {(end - start):.2f} seconds!")

    def make_videos(self, name: str, steps: List[str]) -> None:
        try:
            os.mkdir(name)
        except:
            print("Directory already exists.")

        for i in range(len(steps)):
            prompt=steps[i]

            # get first video in batch
            # started as 25 inference steps
            video_frames = self.pipe(prompt, num_inference_steps=self.fps * self.quality + 1).frames[0] 
            video_path = export_to_video(video_frames, fps=self.fps, output_video_path=f"./{name}/step-{i+1}.mp4")
            video_name = video_path
            print("Name", video_name)
            torch.cuda.empty_cache()

if __name__ == "__main__":
    damo = DAMO_MODEL()
    damo.make_videos(name="BREAD", steps=BREAD_STEPS)
    damo.make_videos(name="BAD BREAD", steps=BAD_BREAD_STEPS)