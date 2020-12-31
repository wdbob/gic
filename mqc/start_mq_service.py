import json
import os
import subprocess
import time

def run():
    print(os.path.dirname(__file__))
    json_fn = os.path.join(os.path.dirname(__file__), 'mq_config.json')
    with open(json_fn, 'r') as f:
        params = json.load(f)
        
    cmd = "docker run --net host --name zoo -p 2181:2181 -p 2888:2888 -p 3888:3888 registry.cn-shanghai.aliyuncs.com/wangxb/kafka-zookeeper:v1"
    cmd = cmd.split(' ')
    subprocess.Popen(cmd)
    time.sleep(60)
    cmd = "docker run --name broker -p 9092:9092 -e EXTIP="+params['external_ip']+" -e INTIP="+params['internal_ip']+" --net host -e KAFKA_TOPICS="+params['topics']+" registry.cn-shanghai.aliyuncs.com/wangxb/kafka-broker:v1"
    cmd = cmd.split(' ')
    subprocess.Popen(cmd)


if __name__ == "__main__":
    run()