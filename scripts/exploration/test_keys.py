from codomyrmex.multimodal.image_generation import ImageGenerator

ig = ImageGenerator()
res = ig.generate(prompt="A test image", model="imagen-3.0-generate-001", number_of_images=1)
if res: print("IMAGE Result:", res)

from codomyrmex.video.generation.video_generator import VideoGenerator

vg = VideoGenerator()
res2 = vg.generate(prompt="A test video", model="veo-2.0-generate-001", duration_seconds=5)
if res2: print("VIDEO Result:", res2)
