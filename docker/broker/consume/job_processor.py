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
        self.ping_proc = None
        self.sent_running_email = False
        self.sent_submit_email = False
        self.send_finish_email = False
            
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

    @classmethod
    def _write_command(cls, job):
        write_path = '/tmp/command_out'
        if os.path.exists(write_path):
            message = job.as_command
            print(message)
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
        job.set_info("command")
        Processor._write_command(job)
        

    def _send_ping(self, job):
        job.set_info("ping")
        Processor._write_command(job)

    @classmethod
    def _send_ok(cls, job):
        job.set_info("ok")
        Processor._write_command(job)
        
    def process(self, job, runner_status, email_params):
        sub = u'来自GPU集群管理系统的消息'
        status = runner_status['status']
        if not job.is_valid() and job.has_email():
            send_email(job.email, sub, email_params, 'submit_failure', job.name)
        elif job.is_valid():
            runner_controller = InstanceController(job.secret, job.key, job.runner_id)
            if (status=="UNKNOWN"):
                status = runner_controller.get_status()
                if (status=='RUNNING'):
                    status = "RUNNER_IN_ORDER"
            if (status=="STOPPED" or status=="STOPPING"):
                runner_controller.start()
                self.connect(job, runner_status)
            elif (status=="NOT_CONNECTED" or status=="RUNNER_IN_ORDER"):
                self.connect(job, runner_status)
            elif self.ping_proc is not None:
                self.ping_proc.terminate()
                self.ping_proc = None

            if (status=="FREE"):
                self._send_command(job)
                """
                if not self.sent_submit_email:
                    send_email(job.email, sub, email_params, 'submit_succeed', job.name)
                    self.sent_submit_email = True
                """
            elif (status=="RUNNING"):
                if not self.sent_running_email:
                    send_email(job.email, sub, email_params, 'running', job.name)
                    self.sent_running_email = True
            elif (status=="FINISHED"):
                self._send_ok(job)
            elif (status=="JOB_FAILED"):
                note = runner_status['note']
                send_running_failure(job, email_params, note)
                return True
            elif (status=="INNER_ERROR"):
                send_inner_error(job, email_params)
            elif (status=="FINISHED_AND_RUNNING"):
                if not self.send_finish_email:
                    note = runner_status['note']
                    if note:
                        send_email(job.email, sub, email_params, 'finish', job.name, note)
                    else:
                        send_email(job.email, sub, email_params, 'finish', job.name)
                    self.send_finish_email = True
                return True
        return False

    @classmethod
    def general_process(cls, runner_status, email_params):
        status = runner_status['status']
        runner_id = runner_status['instance_id']
        if (status=="FINISHED"):
            job = Job.get_dummy_job()
            job.set_instance_id(runner_id)
            cls._send_ok(job)

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

def send_running_failure(job, params, note=None):
    if job.has_email():
        sub = u'来自GPU集群管理系统的消息'
        send_email(job.email, sub, params, 'running_failure', job.name, note)

def send_inner_error(job, params):
    if job.has_email():
        sub = u'来自GPU集群管理系统的消息'
        send_email(job.email, sub, params, 'inner_error', job.name)

class Job:
    job_id = 0
    def __init__(self, info_str, info=None, is_dummy=False):
        self.job = self._get_job_info(info_str)
        if is_dummy:
            self.job_id = -1
        else:
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

    def set_info(self, info):
        self.job['info'] = info

    def set_instance_id(self, instance_id):
        self.job['instance_id'] = instance_id

    @classmethod
    def get_dummy_job(cls):
        command = {
            "git_url": None,
            "username": None,
            "project_name": None,
            "entrypoint": None,
            "language": None,
            "instance_id": None,
            "job_id": -1,
        }
        return Job(None, command, is_dummy=True)

    @property
    def as_command(self):
        command = {
            "info": self.job['info'],
            "git_url": self.job['git_url'],
            "job_id": self.job_id,
            "entrypoint": self.job['entrypoint'],
            "username": self.job['username'],
            "project_name": self.job['project_name'],
            "instance_id": self.job['instance_id'],
            "language": self.job['language']
        }
        if 'log' in self.job.keys():
            command['log'] = self.job['log']
        if 'output' in self.job.keys():
            command['output'] = self.job['output']
        if 'gpu_version' in self.job.keys():
            command['gpu_version'] = self.job['gpu_version']

        command = json.dumps(command)
        command += '\n'
        return command

    @property
    def info(self):
        try:
            return self.job['info']
        except:
            return None

    @property
    def language(self):
        return self.job['language']

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

    @property
    def gpu_version(self):
        try:
            return self.job['gpu_version']
        except:
            return None

def send_email(email, subject, params, content='submit_failure', job_name="", note=None):
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
        content_tmp = u"<html><h1>你的任务【"+job_name+u"】提交成功！！<p>GPU 服务器即将处理任务。"
        msgTest=MIMEText(content_tmp, 'html', 'utf-8')
    elif(content=='running'):
        content_tmp = u"<html><h1>你的任务【"+job_name+u"】正在执行！！<p>GPU 服务器正在处理任务。"
        msgTest=MIMEText(content_tmp, 'html', 'utf-8')
    elif(content=='finish'):
        content_tmp = u"<html><h1>你的任务【"+job_name+u"】完成了！！<p>日志和输出文件保存在附件中。"
        msgTest=MIMEText(content_tmp, 'html', 'utf-8')
    elif(content=='running_failure'):
        msgTest=MIMEText(u"<html><h1>你的任务【"+job_name+u"】执行失败了！！"  
                        u'''<p>请查看你的代码和输出记录'''  
                        ,'html','utf-8')
    elif(content=='inner_error'):
        msgTest=MIMEText(u"<html><h1>你的任务【"+job_name+u"】执行执行时发生错误"  
                        u'''<p>这可能是你的配置问题，也可能是系统bug'''  
                        u'''<p>系统维护者的邮箱是xingbo.wang@winndoo.com'''
                        ,'html','utf-8')
    else:
        msgTest=MIMEText(u'''<html><h1>你的任务【'''+job_name+u'''】提交成功！！'''
                        u'''<p>GPU 服务器即将处理任务'''
                        , 'html', 'utf-8')
    msg.attach(msgTest)  

    if note:
        output = note['output']
        log = note['log']
        name = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
        if output:
            output = output.encode()
            output = MIMEText(output, 'base64', 'utf-8')
            output["Content-Type"] = 'application/octet-stream'
            output["Content-Disposition"] ='attachment; filename="'+name+'.output"'
            msg.attach(output)
        if log:
            log = log.encode()
            log = MIMEText(log, 'base64', 'utf-8')
            log["Content-Type"] = 'application/octet-stream'
            log["Content-Disposition"] ='attachment; filename="'+name+'.log"'
            msg.attach(log)

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