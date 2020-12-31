import json
import os
import subprocess
import time

def run():
    json_fn = os.path.join(os.path.dirname(__file__), 'mq_config.json') 
    with open(json_fn, 'r') as f:
        params = json.load(f)

    server, port = params['internal_ip'].split(':')
    topics = params['topics'].split(',')
    from_begin = params['from_begin']
    pros = []
    for topic in topics:
        read_path = "/tmp/"+topic+"_in"
        if os.path.exists(read_path):
            os.remove(read_path)
        
        # os.mkfifo(read_path)
        cmd = "docker run -e KAFKA_SERVER="+server+ \
            " -e KAFKA_SERVER_PORT="+port+ \
            " -e KAFKA_CONSUMER_TOPIC="+topic+ \
            " --name consumer_"+topic+ \
            " registry.cn-shanghai.aliyuncs.com/wangxb/kafka-consumer:v1"
        cmd = cmd.split(' ')
        p = subprocess.Popen(cmd)
        pros.append(p)
    while True:
        for p in pros:
            print(p.stdout)
        time.sleep(10)


if __name__ == "__main__":
    run()