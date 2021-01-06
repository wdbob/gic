import subprocess
import os 
import json

# change for the server ip if you run it on broker server
def run():
    json_fn = os.path.join(os.path.dirname(__file__), 'mq_config.json')
    with open(json_fn, 'r') as f:
        params = json.load(f)
    cmd = "docker stop producer-command"
    subprocess.call(cmd, shell=True)
    cmd = "docker rm producer-command"
    subprocess.call(cmd, shell=True)

    cmd = "docker run --restart=always -v /tmp:/tmp -e KAFKA_BROKER_SERVER="+params['external_ip']+" -e KAFKA_TOPICS=command --name producer-command registry.cn-shanghai.aliyuncs.com/wangxb/kafka-producer:v1"
    cmd = cmd.split(' ')
    subprocess.Popen(cmd)

if __name__ == "__main__":
    run()