#!/usr/bin/python  
# -*- coding: utf-8 -*-

import json
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
from email.header import Header  
import os,time,re  

class Processor:
    def __init__(self):
        json_fn = os.path.join(os.path.dirname(__file__), 'mq_config.json')
        with open(json_fn, 'r') as f:
            self.params = json.load(f)

    def _parse(self, msg):
        sub = u'来自GPU集群管理系统的消息'
        ret = []
        if msg is None:
            print('message is None')
            return []
        else:
            tmp = msg.split('\n')
            print('tmp:', tmp)
            for m in tmp:
                try:
                    job = self._get_job_info(m)
                    if job is not None :
                        if self._is_intact(job):
                            ret.append(job)
                            if 'email' in job.keys():
                                send_email(job['email'], sub, self.params, 'submit_succeed', job['job_name'])
                        elif 'email' in job.keys():
                            send_email(job['email'], sub, self.params, 'submit_failure', job['job_name'])
                except Exception as e:
                    print('读取job配置信息失败!', e)
        return ret
            
    def _get_job_info(self, info_str):
        info = json.loads(info_str)
        return info

    def _is_intact(self, job_info):
        required_keys = ['username', 
            'git_url', 
            'entrypoint',
            'calculator_ip',
            'account',
            'password',
        ]
        for key in required_keys:
            if key not in job_info.keys():
                return False
        return True

    def _start(self):
        pass

    def process(self, msg):
        self.jobs = self._parse(msg)
        print('jobs:', self.jobs)

    def _start_calculator(self):
        pass

def send_email(email, subject, params, content='submit_failure', job_name=""):
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
        msgTest=MIMEText(u"<html><h1>你的任务("+job_name+u")提交失败了！！"  
                        u'''<p>请查看你的任务配置文件'''  
                        ,'html','utf-8')  
    elif(content=='submit_succeed'):
        content_tmp = u"<html><h1>你的任务("+job_name+u")提交成功！！<p>GPU 服务器即将处理任务"
        msgTest=MIMEText(content_tmp, 'html', 'utf-8')
    else:
        msgTest=MIMEText(u'''<html><h1>你的任务('''+job_name+u''')提交成功！！'''
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
    processor = Processor()
    processor.process(message)