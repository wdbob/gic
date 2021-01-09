import json
import os
import subprocess
import time
from multiprocessing import Process, Queue


def run():

    env_dict = os.environ
    broker_server = env_dict['KAFKA_BROKER_SERVER']
    topics = env_dict['KAFKA_TOPICS']
    topics = topics.split(',')

    pros = {}

    for topic in topics:
        cmd = "/usr/kafka_consumer/bin/kafka-console-consumer.sh --topic "+topic+\
            " --bootstrap-server " +broker_server
        cmd = cmd.split(' ')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        pros[topic] = p

    while True:
        for p in pros:
            if (p=='command'):
                process = pros['command']
                output = process.stdout.readline()
                if output:
                    output = output.decode()
                    print(output.strip())
        time.sleep(1)


if __name__ == "__main__":
    run()