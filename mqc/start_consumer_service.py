import json
import os
import subprocess

def run():
    json_fn = os.path.join(os.path.dirname(__file__), 'mq_config.json') 
    with open(json_fn, 'r') as f:
        params = json.load(f)

    server, port = params['internal_ip'].split(':')
    topics = params['topics'].split(',')
    from_begin = params['from_begin']
    print(topics)
    for topic in topics:
        read_path = "/tmp/"+topic+"_in"
        if os.path.exists(read_path):
            os.remove(read_path)
        
        os.mkfifo(read_path)
        cmd = "docker run -e KAFAK_SERVER="+server+ \
            " -e KAFKA_SERVER_PORT="+port+ \
            " -e KAFKA_CONSUMER_TOPIC="+topic+ \
            " -e KAFKA_CONSUMER_FROME_BEGINNING="+from_begin+ \
            " registry.cn-shanghai.aliyuncs.com/wangxb/kafka-consumer:v1 > "+read_path
        print(cmd)
        cmd = cmd.split(' ')
        subprocess.Popen(cmd)


if __name__ == "__main__":
    run()