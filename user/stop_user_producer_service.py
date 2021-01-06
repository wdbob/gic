import subprocess
import os 
import json

def run():
    json_fn = os.path.join(os.path.dirname(__file__), 'mq_config.json')
    with open(json_fn, 'r') as f:
        params = json.load(f)
    cmd = "docker stop producer-jobs"
    subprocess.call(cmd, shell=True)
    cmd = "docker rm producer-jobs"
    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    run()