import subprocess
import os
import time
from command_processor import Processor

def run():
    env_dict = os.environ
    broker_server = env_dict['KAFKA_BROKER_SERVER']

    # start consumer with topic command
    cmd = "docker stop consumer-command"
    subprocess.call(cmd, shell=True)
    cmd = "docker rm consumer-command"
    subprocess.call(cmd, shell=True)
    cmd = "docker stop producer-status"
    subprocess.call(cmd, shell=True)
    cmd = "docker rm producer-status"
    subprocess.call(cmd, shell=True)
    cmd = "docker run --name consumer-command --rm -v /tmp:/tmp -e KAFKA_BROKER_SERVER="+broker_server+ \
        " -e KAFKA_TOPICS=command -t " +\
        "registry.cn-shanghai.aliyuncs.com/wangxb/kafka-runner-consumer:v1"
    print(cmd)
    cmd = cmd.split(' ')
    p_consumer_command = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    # start producer with topic status
    cmd = "docker run --restart=always --name producer-status -v /tmp:/tmp -e KAFKA_BROKER_SERVER="+broker_server+ \
        " -e KAFKA_TOPICS=status " +\
        "registry.cn-shanghai.aliyuncs.com/wangxb/kafka-producer:v1"
    print(cmd)
    cmd = cmd.split(' ')
    subprocess.Popen(cmd)
    time.sleep(10)

    command_processor = Processor()

    while True:
        output = p_consumer_command.stdout.readline()
        if output:
            output = output.decode()
            output = output.strip()
            print(output) 
            command_processor.process(output)
        time.sleep(0.1)


if __name__ == "__main__":
    run()