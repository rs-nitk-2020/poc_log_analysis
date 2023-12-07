import os
import time
import socket
import webbrowser
from contextlib import closing

def find_free_port():
    """
    Finds a free port on the host machine
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

def run_server():
    free_port = find_free_port()
    free_port = 8000
    cmd = f"python3 manage.py runserver 0.0.0.0:{free_port} --noreload &"
    
    # Run the server as a background process
    os.system(f"nohup {cmd} > /dev/null 2>&1 &")

    # Provide the URL in the console for manual access
    url = f"http://0.0.0.0:{free_port}/"
    print(f"Server is running in the background.")
    print(f"You can access the site at: {url}")

if __name__ == "__main__":
    run_server()
    while True: 
        time.sleep(1000)
