import subprocess
import os

temp_dir = "/tmp"

cmd = [
    "docker", "run", "--rm", "--network=none", "--cap-drop=ALL",
    "--security-opt=no-new-privileges", "--read-only", "--memory=256m",
    "--memory-swap=256m", "--cpus=0.5", "--pids-limit=50",
    f"--security-opt=seccomp={os.path.abspath('src/codomyrmex/coding/sandbox/seccomp_profile.json')}",
    f"--user={os.getuid()}:{os.getgid()}",
    "-v", f"{temp_dir}:/sandbox",
    "-w", "/sandbox",
    "python:3.9-slim",
    "python", "-c", "print('hello')"
]
print("Running command:", " ".join(cmd))
result = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", result.returncode)
print("Stdout:", result.stdout)
print("Stderr:", result.stderr)
