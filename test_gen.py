from codomyrmex.video.generation.video_generator import VideoGenerator
from codomyrmex.multimodal.image_generation import ImageGenerator
print("Generating Image...")
ig = ImageGenerator()
res = ig.generate(prompt="A test image", model="imagen-3.0-generate-001", number_of_images=1)
if res: print("Image Keys:", res[0].keys())

print("Generating Video...")
vg = VideoGenerator()
res2 = vg.generate(prompt="A test video", model="veo-2.0-generate-001", duration_seconds=5)
if res2: print("Video Keys:", res2[0].keys())
