import urllib.request

try:
    urllib.request.urlopen("https://github.com/indygreg/python-build-standalone/releases/download/20241206/cpython-3.11.11%2B20241206-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz")
    print("Success")
except Exception as e:
    print(f"Error: {e}")
