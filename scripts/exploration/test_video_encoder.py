import imageio
import numpy as np

try:
    writer = imageio.get_writer("output/test_encoding.mp4", fps=20)
    for i in range(20):
        # Red frame
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[:, :, 0] = 255
        writer.append_data(frame)
    writer.close()
    print("MP4 Generation Success!")
except Exception as e:
    print(f"Failed to generate MP4: {e}")
