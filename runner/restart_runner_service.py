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

    json_fn = os.path.join(os.path.dirname(__file__), 'mq_config.json')
    with open(json_fn, 'r') as f:
        params = json.load(f)

    cmd = "docker run --restart=always -v /tmp:/tmp -v /workspace:/workspace -e KAFKA_BROKER_SERVER=" \
        +params['server_ip']+ " -e INSTANCE_ID="+params['instance_id']+\
        " -v /var/run/docker.sock:/var/run/docker.sock --name runner-dind registry.cn-shanghai.aliyuncs.com/wangxb/dind-runner:v1"
    cmd = cmd.split(' ')
    subprocess.Popen(cmd)


if __name__ == "__main__":
    run()