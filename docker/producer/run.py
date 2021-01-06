import os
import subprocess
import time
import signal

def my_handler(signum, frame):
    global stop
    stop = True

def run():
    signal.signal(signal.SIGINT, my_handler)
    signal.signal(signal.SIGHUP, my_handler)
    signal.signal(signal.SIGTERM, my_handler)
    global stop
    stop = False

    env_dict = os.environ
    broker_server = env_dict['KAFKA_BROKER_SERVER']
    topic = env_dict['KAFKA_TOPICS']
    write_path = "/tmp/"+topic+"_out"
    if os.path.exists(write_path):
        os.remove(write_path)
    os.mkfifo(write_path)
    cmd = "chmod 777 "+write_path
    subprocess.call(cmd, shell=True)
    cmd1 = "cat "+write_path
    cmd1 = cmd1.split(' ')
    p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
    cmd2 = "/usr/origin/bin/kafka-console-producer.sh --topic "+topic+" --bootstrap-server "+broker_server
    print(cmd2)
    cmd2 = cmd2.split(' ')
    p2 = subprocess.Popen(cmd2, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print('wait for starting producer.')
    time.sleep(10)
    print('start to receive messages.')
    while True:
        if stop:
            os.remove(write_path)
            break

        #for line in p1.stdout.readlines():
            #print(line)
        p1_output = p1.stdout.readlines()
        p2.stdin.writelines(p1_output)
        p2.stdin.flush()
        p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)    


if __name__ == "__main__":
    run()