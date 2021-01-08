import subprocess
import os 
import json

def run():
    cmd = "docker stop producer-status"
    subprocess.call(cmd, shell=True)
    cmd = "docker rm producer-status"
    subprocess.call(cmd, shell=True)
    cmd = "docker stop consumer-command"
    subprocess.call(cmd, shell=True)
    cmd = "docker rm consumer-command"
    subprocess.call(cmd, shell=True)
    cmd = "docker stop runner-dind"
    subprocess.call(cmd, shell=True)
    cmd = "docker rm runner-dind"
    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    run()