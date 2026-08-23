import subprocess
print(subprocess.run(["docker", "ps"], capture_output=True, text=True).stdout)
