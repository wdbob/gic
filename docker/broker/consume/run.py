import json
import os
import subprocess
import time
import signal
from multiprocessing import Process, Queue
from base64 import b64decode

from job_processor import Processor, Job, send_failure
from instance_controller import InstanceController
from decrypt import decrypt_long

# process jobs from user, and send command to runner
def process_jobs(process, q):
    output = process.stdout
    ssh_dir = os.path.join('/root', '.ssh', 'gic')
    for line in iter(output.readline, ''):
        if line:
            line = line.decode().strip()
            line = b64decode(line)
            line = decrypt_long(line, ssh_dir)
            q.put(line)
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
    
    pros = {}
    processor_list = {}
    all_jobs = {}
    runner_job_list = {}
    runner_status_list = {}
    runner_controller_list = {}
    clock_list = {}
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
                """
                print('new job --------------')
                print(job.job_id)
                """
                status = {
                        "status": "UNKNOWN",
                        "job_id": job.job_id,
                        "instance_id": job.runner_id,
                        "note": None
                }
                runner_status_list[job.runner_id] = status
                if job.runner_id not in runner_job_list.keys():
                    runner_job_list[job.runner_id] = {}
                if job.runner_id not in runner_controller_list.keys():
                    ctl = InstanceController(job.secret, job.key, job.runner_id)
                    runner_controller_list[job.runner_id] = ctl
                processor = Processor()
                processor_list[job.job_id] = processor
                
                processor.process(job, runner_status_list[job.runner_id], email_params)
                runner_job_list[job.runner_id][job.job_id] = job
                all_jobs[job.job_id] = job
            else:
                send_failure(job, email_params)

        if not q_status.empty():
            status = q_status.get()
            """
            print('------')
            print(status)
            print('------')
            """
            status = json.loads(status)
            if status['job_id'] not in all_jobs.keys():
                job = None
            else: 
                job = all_jobs[status['job_id']]
            if status['job_id'] in processor_list.keys():
                processor = processor_list[status['job_id']]
                finished = processor.process(job, status, email_params)
            else:
                Processor.general_process(status, email_params)
                finished = False
            if finished:
                del runner_job_list[job.runner_id][job.job_id]
                del all_jobs[job.job_id]
                del processor_list[job.job_id]
            runner_status_list[status['instance_id']] = status

        # shut down the runner, which is free more than 300s
        for runner in runner_status_list:
            status = runner_status_list[runner]
            #print('------- shut down')
            #print(runner, status)
            if (status['status']=='FREE'):
                now = time.time()
                if runner in clock_list.keys():
                    diff = now-clock_list[runner]
                    if (diff>300):
                        ctl = runner_controller_list[runner]
                        ctl.stop()
                        del clock_list[runner]
                        del runner_status_list[runner]
                        break
                else:
                    clock_list[runner] = now
            else:
                if runner in clock_list.keys():
                    del clock_list[runner]

        time.sleep(1)


if __name__ == "__main__":
    run()