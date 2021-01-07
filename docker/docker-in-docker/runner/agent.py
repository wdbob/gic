import subprocess
import os
import time

def run():
    env_dict = os.environ
    broker_server = env_dict['KAFKA_BROKER_SERVER']

    # consumer with topic command
    cmd = "docker run --rm -v /tmp:/tmp -e KAFKA_BROKER_SERVER="+broker_server+ \
        " -e KAFKA_TOPICS=command " +\
        "registry.cn-shanghai.aliyuncs.com/wangxb/kafka-runner-consumer:v1"
    cmd = cmd.split(' ')
    p_consumer_command = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    # producer with topic status
    cmd = "docker run --rm -v /tmp:/tmp -e KAFKA_BROKER_SERVER="+broker_server+ \
        " -e KAFKA_TOPICS=status" +\
        "registry.cn-shanghai.aliyuncs.com/wangxb/kafka-producer:v1"
    cmd = cmd.split(' ')
    p_producer_status = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    while True:
        time.sleep(1)



if __name__ == "__main__":
    run()