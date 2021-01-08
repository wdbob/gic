import json
import os
import subprocess
import time
from multiprocessing import Process, Queue

#from command_processor import Processor

"""
def command_jobs(process, processor):
    output = process.stdout
    for line in iter(output.readline, ''):
        line = bytes.decode(line)
        if (line is not None and line!=''):
            processor.process(line)
"""

def run():

    env_dict = os.environ
    broker_server = env_dict['KAFKA_BROKER_SERVER']
    topics = env_dict['KAFKA_TOPICS']
    topics = topics.split(',')

    """
    processor = Processor()
    """
    pros = {}

    for topic in topics:
        cmd = "/usr/kafka_consumer/bin/kafka-console-consumer.sh --topic "+topic+\
            " --bootstrap-server " +broker_server
        cmd = cmd.split(' ')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        pros[topic] = p

    """
    command_process = Process(target=command_jobs, args=(pros['command'], processor))
    command_process.start()
    """

    while True:
        for p in pros:
            if (p=='command'):
                """
                if not command_process.is_alive():
                    try:
                        command_process.start()
                    except Exception as e:
                        print(e)
                """
                process = pros['command']
                """
                output = process.stdout
                for line in iter(output.readline, ''):
                    # 会陷入这个循环中，因为它一直等待输入
                    if (line is not None and line!=''):
                        print(line)
                """
                output = process.stdout.readline()
                if output:
                    output = output.decode()
                    print(output.strip())
        time.sleep(1)


if __name__ == "__main__":
    run()