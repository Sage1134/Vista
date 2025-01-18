# pip install diffusers transformers accelerate opencv-python
# pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

import time
import torch
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.utils import export_to_video

# example user inputs, from asker and receiver
from bread_example import BREAD_STEPS, HOW_QUESTION, HOW_TO_BAKE_BREAD

print("Loading model...")
start = time.time()
pipe = DiffusionPipeline.from_pretrained("damo-vilab/text-to-video-ms-1.7b", torch_dtype=torch.float16, variant="fp16")
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_model_cpu_offload()

end = time.time()
print(f"Model loaded in {(end - start):.2f} seconds!")

for i in range(len(BREAD_STEPS)):
    prompt=BREAD_STEPS[i]
    video_frames = pipe(prompt, num_inference_steps=25).frames[0] # get first video in batch
    video_path = export_to_video(video_frames, fps=10, output_video_path=f"step-{i}.mp4")
    video_name = video_path
    print("Name", video_name)
    torch.cuda.empty_cache()