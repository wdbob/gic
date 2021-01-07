import json
import os
import subprocess
import time
import signal
from multiprocessing import Process, Queue

from job_processor import Processor


def process_jobs(process, processor):
    output = process.stdout
    for line in iter(output.readline, ''):
        line = bytes.decode(line)
        if (line is not None and line!=''):
            processor.process(line)

def run():

    env_dict = os.environ
    broker_server = env_dict['KAFKA_BROKER_SERVER']
    topics = env_dict['KAFKA_TOPICS']
    topics = topics.split(',')

    processor_params = {}
    processor_params['proc_email'] = env_dict['EMAIL']
    processor_params['proc_smtpserver'] = env_dict['SMTPSERVER']
    processor_params['proc_email_username'] = env_dict['EMAIL']
    processor_params['proc_email_password'] = env_dict['EMAIL_PASSWORD']
    
    processor = Processor(processor_params)
    pros = {}

    for topic in topics:
        cmd = "/usr/kafka_consumer/bin/kafka-console-consumer.sh --topic "+topic+\
            " --bootstrap-server " +broker_server
        cmd = cmd.split(' ')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        pros[topic] = p

    job_process = Process(target=process_jobs, args=(pros['jobs'], processor))
    job_process.start()
    while True:
        for p in pros:
            if (p=='jobs'):
                if not job_process.is_alive():
                    try:
                        job_process.start()
                    except Exception as e:
                        print(e)

            elif(p=='status'):
                pass
        time.sleep(1)


if __name__ == "__main__":
    run()