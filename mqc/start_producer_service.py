import subprocess
import os 
import json

def run():
    json_fn = os.path.join(os.path.dirname(__file__), 'mq_config.json')
    with open(json_fn, 'r') as f:
        params = json.load(f)

    cmd = "sudo docker run -v /tmp:/tmp -e KAFKA_BROKER_SERVER="+params['external_ip']+" -e KAFKA_TOPICS="+params['topics']+" --name producer wangziling100/kafka:producer"
    cmd = cmd.split(' ')
    subprocess.Popen(cmd)

if __name__ == "__main__":
    run()