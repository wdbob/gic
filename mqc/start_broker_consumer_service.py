import json
import os
import subprocess
import time

from job_processor import Processor

def run():
    json_fn = os.path.join(os.path.dirname(__file__), 'mq_config.json') 
    with open(json_fn, 'r') as f:
        params = json.load(f)

    server, port = params['internal_ip'].split(':')
    topics = params['topics'].split(',')
    from_begin = params['from_begin']
    for topic in topics:
        cmd = "docker stop consumer_"+topic
        subprocess.call(cmd, shell=True)
        cmd = "docker rm consumer_"+topic
        subprocess.call(cmd, shell=True)
    processor = Processor()
    pros = {}

    for topic in topics:
        cmd = "docker run -e KAFKA_SERVER="+server+ \
            " -e KAFKA_SERVER_PORT="+port+ \
            " -e KAFKA_CONSUMER_TOPIC="+topic+ \
            " --name consumer_"+topic+ \
            " registry.cn-shanghai.aliyuncs.com/wangxb/kafka-consumer:v1"
        cmd = cmd.split(' ')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        pros[topic] = p

    while True:
        for p in pros:
            if (p=='jobs'):
                output = pros[p].stdout
                print('jobs here')
                for line in output.readlines():
                    print(line)
                    if line is not None:
                        processor.process(line)
            elif(p=='status'):
                pass
        time.sleep(10)


if __name__ == "__main__":
    run()