#!/usr/bin/python  
# -*- coding: utf-8 -*-

import json
from multiprocessing import Process
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
from email.header import Header  
import os,time,re  
from instance_controller import InstanceController

class Processor:
    def __init__(self):
        """
        if params is None:
            json_fn = os.path.join(os.path.dirname(__file__), 'mq_config.json')
            with open(json_fn, 'r') as f:
                self.params = json.load(f)
        else:
            self.params = params
        """
        self.ping_proc = None
        pass

    """
    def _parse(self, msg):
        sub = u'来自GPU集群管理系统的消息'
        ret = []
        if msg is None :
            print('message is None')
            return []
        else:
            tmp = msg.split('\n')
            print('tmp:', tmp)
            for m in tmp:
                if(m==''): continue
                try:
                    job = Job(m)
                    if job.is_valid():
                        ret.append(job)
                        if job.has_email():
                            send_email(job.email, sub, self.params, 'submit_succeed', job.name)
                    elif job.has_email():
                        send_email(job.email, sub, self.params, 'submit_failure', job.name)
                except Exception as e:
                    print('读取job配置信息失败!', e)
                    break
        return ret
    """
            
    def _get_job_info(self, info_str):
        info = json.loads(info_str)
        return info

    def _is_intact(self, job_info):
        required_keys = ['username', 
            'git_url', 
            'entrypoint',
            'key',
            'secret',
            'instance_id',
        ]
        for key in required_keys:
            if key not in job_info.keys():
                return False
        return True

    def _write_command(self, command):
        write_path = '/tmp/command_out'
        if os.path.exists(write_path):
            message = job.as_command
            # set job
            try:
                f = os.open(write_path, os.O_WRONLY)
                os.write(f, message.encode())
                os.close(f)
            except Exception as e:
                print(e)
                os.close(f)
        else:
            print("主题为command的生产者服务没有启动，请先启动生产者服务")

    def _send_command(self, job):
        job['info'] = "command"
        self._write_command(job)
        

    def _send_ping(self, job):
        job['info'] = "ping"
        self._write_command(job)

    def _send_ok(self, job):
        job['info'] = "ok"
        self._write_command(job)
        
    """
    def process(self, msg):
        self.jobs = self._parse(msg)
        for job in self.jobs:
            self._write_command(job)
    """
    def process(self, job, runner_status, email_params):
        sub = u'来自GPU集群管理系统的消息'
        status = runner_status['status']
        if not job.is_valid() and job.has_email():
            send_email(job.email, sub, email_params, 'submit_failure', job.name)
        elif job.is_valid():
            runner_controller = InstanceController(job.secret, job.key, job.runner_id)
            print(job.job, runner_status)
            if (status=="UNKNOWN"):
                status = runner_controller.get_status()
            if (status=="STOPPED"):
                runner_controller.start()
                self.connect(job, runner_status)
            elif (status=="NOT_CONNECTED"):
                self.connect(job, runner_status)
            elif (status=="FREE"):
                if self.ping_proc is not None:
                    self.ping_proc.terminate()
                    self.ping_proc = None
                self._send_command(job)
            elif (status=="FINISHED"):
                self._send_ok(job)
            elif (status=="JOB_FAILED"):
                # TODO
                send_failure(job, email_params)

    def connect(self, job, status, threshold=3):
        def query():
            while True:
                self._send_ping(job)
                time.sleep(threshold)

        if self.ping_proc is None:
            self.ping_proc = Process(target=query)
            self.ping_proc.start()


def send_failure(job, params):
    if job.has_email():
        sub = u'来自GPU集群管理系统的消息'
        send_email(job.email, sub, params, 'submit_failure', job.name)

class Job:
    job_id = 0
    def __init__(self, info_str, info=None):
        self.job = self._get_job_info(info_str)
        self.job_id = Job.job_id
        Job.job_id += 1
        if info is not None:
            self.job = info

    def _get_job_info(self, info_str):
        try:
            info = json.loads(info_str)
        except:
            info = None
        return info

    def _is_intact(self, job_info):
        required_keys = ['username', 
            'git_url', 
            'entrypoint',
            'key',
            'secret',
            'instance_id',
        ]
        for key in required_keys:
            if key not in job_info.keys():
                return False
        return True
    
    def is_valid(self):
        if self.job is None:
            return False
        return self._is_intact(self.job)
    
    def has_email(self):
        try:
            if 'email' in self.job.keys():
                return True
            return False
        except:
            return False

    @property
    def as_command(self):
        command = {
            "git_url": self.job['git_url'],
            "job_id": self.job_id,
            "entrypoint": self.job['entrypoint'],
            "username": self.job['username'],
        }
        if 'log' in self.job.keys():
            command['log'] = self.job['log']
        if 'output' in self.job.keys():
            command['output'] = self.job['output']

        command = json.dumps(command)
        command += '\n'
        return command

    @property
    def runner_id(self):
        return self.job['instance_id']
    
    @property
    def secret(self):
        return self.job['secret']

    @property
    def key(self):
        return self.job['key']

    @property
    def email(self):
        try:
            return self.job['email']
        except:
            return None

    @property
    def name(self):
        try:
            return self.job['job_name']
        except:
            return None


def send_email(email, subject, params, content='submit_failure', job_name="", text=None):
    #发送邮箱  
    mail_from = params['proc_email']  
    #发送邮件主题  
    mail_subject = subject
    #发送邮箱服务器  
    mail_smtpserver =  params['proc_smtpserver'] 
    #发送邮箱用户/密码  
    mail_username =  params['proc_email_username'] 
    mail_password = params['proc_email_password']  

    mail_to = email
     #创建一个带附件的邮件实例（内容） ent_tmp 

    msg = MIMEMultipart()  
    #将读取到的测试报告的数据以html形式显示为邮件的中文  
    if (content=='submit_failure'):
        msgTest=MIMEText(u"<html><h1>你的任务【"+job_name+u"】提交失败了！！"  
                        u'''<p>请查看你的任务配置文件'''  
                        ,'html','utf-8')  
    elif(content=='submit_succeed'):
        content_tmp = u"<html><h1>你的任务【"+job_name+u"】提交成功！！<p>GPU 服务器即将处理任务"
        msgTest=MIMEText(content_tmp, 'html', 'utf-8')
    else:
        msgTest=MIMEText(u'''<html><h1>你的任务【'''+job_name+u'''】提交成功！！'''
                        u'''<p>GPU 服务器即将处理任务'''
                        , 'html', 'utf-8')
    msg.attach(msgTest)  
    #定义邮件的附件  
    #att1 = MIMEText(open(file_new, 'rb').read(), 'base64', 'utf-8')  
    #att1["Content-Type"] = 'application/octet-stream'  
    #att1["Content-Disposition"] ='attachment; filename="Automation test report.html"'#这里的filename指的是附件的名称及类型  
    #msg.attach(att1)  
    #将邮件的主题等相关信息添加到邮件实例  
    msg['Subject'] = Header(mail_subject)  
    msg['From'] = mail_from  
    msg['To'] = mail_to  
    msg['date']=time.strftime('%a, %d %b %Y %H:%M:%S %z')   
    #创建发送服务器实例并将发送服务器添加到实例中  
    smtp = smtplib.SMTP()  
    smtp.connect(mail_smtpserver)  
    smtp.login(mail_username, mail_password)  
    smtp.sendmail(mail_from, mail_to, msg.as_string())  
    smtp.quit()  


if __name__ == "__main__":
    env_dict = os.environ
    broker_server = env_dict['KAFKA_BROKER_SERVER']
    topics = env_dict['KAFKA_TOPICS']
    topics = topics.split(',')

    processor_params = {}
    processor_params['proc_email'] = env_dict['EMAIL']
    processor_params['proc_smtpserver'] = env_dict['SMTPSERVER']
    processor_params['proc_email_username'] = env_dict['EMAIL']
    processor_params['proc_email_password'] = env_dict['EMAIL_PASSWORD']
    #send_email('xingbo.wang@winndoo.com', 'test')
    message = {
        "username": "wangxb",
        "git_url": "test.gi",
        "entrypoint": "abc.py",
        "email": "xingbo.wang@winndoo.com",
        "job_name": "测试任务",
        "output": None,
        "calculator_ip": "10.0.0.1",
        "account": "wangxb",
        "password": "1234",
        "log": "test.log"
    }
    message = json.dumps(message)
    job = Job(message)
    processor = Processor()