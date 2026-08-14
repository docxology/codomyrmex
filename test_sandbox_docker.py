from codomyrmex.coding.sandbox.container import DockerSandbox
sandbox = DockerSandbox(timeout=10, network="none", read_only=True)
res = sandbox.execute("python", "print('hello world')")
print(res)
