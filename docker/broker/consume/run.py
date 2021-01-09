import json
import os
import subprocess
import time
import signal
from multiprocessing import Process, Queue

from job_processor import Processor, Job, send_failure

# process jobs from user, and send command to runner
def process_jobs(process, q):
    output = process.stdout
    for line in iter(output.readline, ''):
        if line:
            line = line.decode()
            q.put(line.strip())
        """
        line = bytes.decode(line)
        if (line is not None and line!=''):
            processor.process(line)
        """

def process_status(process, q):
    output = process.stdout
    for line in iter(output.readline, ''):
        if line:
            line = line.decode()
            q.put(line.strip())

def run():

    env_dict = os.environ
    broker_server = env_dict['KAFKA_BROKER_SERVER']
    topics = env_dict['KAFKA_TOPICS']
    topics = topics.split(',')

    email_params = {}
    email_params['proc_email'] = env_dict['EMAIL']
    email_params['proc_smtpserver'] = env_dict['SMTPSERVER']
    email_params['proc_email_username'] = env_dict['EMAIL']
    email_params['proc_email_password'] = env_dict['EMAIL_PASSWORD']
    
    #processor = Processor(processor_params)
    pros = {}
    processor_list = {}
    all_jobs = {}
    runner_job_list = {}
    runner_status_list = {}
    q_jobs = Queue()
    q_status = Queue()

    for topic in topics:
        cmd = "/usr/kafka_consumer/bin/kafka-console-consumer.sh --topic "+topic+\
            " --bootstrap-server " +broker_server
        cmd = cmd.split(' ')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        pros[topic] = p

    job_process = Process(target=process_jobs, args=(pros['jobs'], q_jobs))
    job_process.start()
    status_process = Process(target=process_status, args=(pros['status'], q_status))
    status_process.start()
    while True:
        for p in pros:
            if (p=='jobs'):
                if not job_process.is_alive():
                    try:
                        job_process.start()
                    except Exception as e:
                        print(e)
                
            elif(p=='status'):
                if not status_process.is_alive():
                    try:
                        status_process.start()
                    except Exception as e:
                        print(e)

        if not q_jobs.empty():
            job = Job(q_jobs.get())
            if job.is_valid():
                # need to start a new runner
                if job.runner_id not in runner_status_list.keys():
                    status = {
                        "status": "UNKNOWN",
                        "job_id": None,
                        "instance_id": None,
                        "note": None
                    }
                    runner_status_list[job.runner_id] = status
                    runner_job_list[job.runner_id] = []
                processor = Processor()
                processor_list[job.job_id] = processor
                
                """
                if (runner_status_list[job.runner_id] == "NOT_CONNECTED"):
                    processor.connect(job)
                elif (runner_status_list[job.runner_id] == "FREE"):
                    pass
                """
                processor.process(job, runner_status_list[job.runner_id], email_params)
                runner_job_list[job.runner_id].append(job)
                all_jobs[job.job_id] = job
            else:
                send_failure(job, email_params)

        if not q_status.empty():
            print(q_status.get())
        time.sleep(1)


if __name__ == "__main__":
    run()