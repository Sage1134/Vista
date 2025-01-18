# pip install diffusers transformers accelerate opencv-python sentencepiece
# pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Too slow for my PC. damo is recommended.

import time
import torch
from diffusers import CogVideoXPipeline
from diffusers.utils import export_to_video
from typing import List

# example user inputs, from asker and receiver
from bread_example import BREAD_STEPS, HOW_QUESTION, HOW_TO_BAKE_BREAD, BAD_BREAD_STEPS
        
class CogVideoX5BModel:
    def __init__(self):
        start = time.time()

        self.pipe = CogVideoXPipeline.from_pretrained(
            "THUDM/CogVideoX-5b",
            torch_dtype=torch.bfloat16
        )

        self.pipe.enable_model_cpu_offload()
        self.pipe.vae.enable_tiling()
        
        end = time.time()
        print(f"Model loaded in {(end - start):.2f} seconds!")

    def make_videos_from_steps(self, name:str, steps:List[str])->None:
        for i in range(len(steps)):
            video = self.pipe(
                prompt=steps[i],
                num_videos_per_prompt=1, # so that .frames[0] gets all our videos
                num_inference_steps=50,
                num_frames=49,
                guidance_scale=6,
                generator=torch.Generator(device='cuda').manual_seed(42)
            ).frames[0]

            export_to_video(video, f"{name}-{i}.mp4", fps=8)

if __name__ == '__main__':
    cogvideoX5b = CogVideoX5BModel()
    cogvideoX5b.make_videos_from_steps("Bake Bread", steps=HOW_TO_BAKE_BREAD)