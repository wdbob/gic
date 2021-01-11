import os
import json
import subprocess


def run():

    json_fn = os.path.join(os.path.dirname(__file__), 'mq_config.json')
    with open(json_fn, 'r') as f:
        params = json.load(f)

    cmd = "docker stop broker-consumer"
    subprocess.call(cmd, shell=True)
    cmd = "docker rm broker-consumer"
    subprocess.call(cmd, shell=True)

    home = os.path.expanduser('~')
    ssh_dir = os.path.join(home, '.ssh', 'gic')
    cmd = "docker run --name broker-consumer --restart=always -e KAFKA_BROKER_SERVER=" + \
        params['server_ip'] + \
        " -e KAFKA_TOPICS=jobs,status -e EMAIL="+ params['proc_email'] + \
        " -e SMTPSERVER="+ params['proc_smtpserver'] + " -e EMAIL_PASSWORD="+ \
        params['proc_email_password'] + \
        " -v /tmp:/tmp -v " +ssh_dir + \
        ":/root/.ssh/gic registry.cn-shanghai.aliyuncs.com/wangxb/kafka-broker-consumer:v1"
    cmd = cmd.split(' ')
    subprocess.Popen(cmd)


if __name__ == "__main__":
    run()