import subprocess
import os 
import json

def run():
    json_fn = os.path.join(os.path.dirname(__file__), 'mq_config.json')
    with open(json_fn, 'r') as f:
        params = json.load(f)

    cmd = "docker run --restart=always -v /tmp:/tmp -v /workspace:/workspace -e KAFKA_BROKER_SERVER=" \
        +params['server_ip']+ \
        " -v /var/run/docker.sock:/var/run/docker.sock --name runner-dind registry.cn-shanghai.aliyuncs.com/wangxb/dind-runner:v1"
    cmd = cmd.split(' ')
    subprocess.Popen(cmd)

if __name__ == "__main__":
    run()