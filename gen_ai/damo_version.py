import time
import torch
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from typing import List
import os

class DAMO_MODEL:
    def __init__(self, fps):
        print("Loading model...")
        start = time.time()
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"================Using device: {device}")

        # Load pipeline
        self.pipe = DiffusionPipeline.from_pretrained(
            "damo-vilab/text-to-video-ms-1.7b",
            torch_dtype=torch.float16,
            variant="fp16"
        ).to(device)

        # Enable faster attention if xFormers is available
        try:
            self.pipe.enable_xformers_memory_efficient_attention()
            print("Enabled xFormers memory-efficient attention.")
        except Exception as e:
            print(f"Could not enable xFormers: {e}")

        # Use a faster scheduler
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
        
        # Offload model to CPU when not in use
        self.pipe.enable_model_cpu_offload()

        self.fps = fps

        end = time.time()
        print(f"Model loaded in {(end - start):.2f} seconds!")

    def make_videos(self, name: str, steps: List[str]) -> None:
        try:
            # Example of fewer steps and smaller resolution for faster generation
            # You can tweak these values as needed
            total_inference_steps = 10  # Fewer steps than the default
            video_height = 128
            video_width = 128

            print(f"Generating video '{name}' with {len(steps)} frames at {self.fps} FPS.")
            for idx, prompt in enumerate(steps):
                print(f"Frame {idx+1}/{len(steps)}: {prompt}")
                self.pipe(prompt,
                          num_inference_steps=total_inference_steps,
                          height=video_height,
                          width=video_width).images

            # ...existing code for saving or exporting the video...
            print(f"'{name}' generation complete.")
        except Exception as e:
            print(f"Error making videos: {e}")
            raise