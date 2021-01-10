#!/usr/bin/python  
# -*- coding: utf-8 -*-  
import json
import os
import subprocess
from multiprocessing import Process
import time


class Processor:
    def __init__(self, instance_id):
        self.connected = False
        self.instance_id = instance_id
        self.status = 'NOT_CONNECTED'
        self.query_proc = None
        self.command_list = {}
    
    def _parse(self, msg):
        ret = []
        if msg is None :
            print('message is None')
            return []
        else:
            tmp = msg.split('\n')
            for m in tmp:
                if(m==''): continue
                try:
                    command = Command(m)
                    if command.instance_id==self.instance_id:
                        ret.append(command)
                except Exception as e:
                    print(e)
                    ret = []
                    break
        return ret

    def _exec(self, command):
        """
        is_connected = self.check_connection(command)
        if is_connected:
        """
        if (command.info=="command"):
            self.status = "RUNNING"
            self.send_status_to_broker(self.status, command)

            if not os.path.exists('/workspace'):
                cmd = "mkdir /workspace"
                subprocess.call(cmd, shell=True)
            namespace_path = os.path.join('/workspace', command.username)
            if not os.path.exists(namespace_path):
                cmd = "mkdir "+namespace_path
                subprocess.call(cmd, shell=True)
            workspace_path = os.path.join(namespace_path, command.project_name)
            if os.path.exists(workspace_path):
                cmd = "cd " + workspace_path +" && git pull"
                subprocess.call(cmd, shell=True)
            else:
                cmd = "cd "+namespace_path +" && git clone "+ command.git_url
                subprocess.call(cmd, shell=True)

            # exec entrypoint
            cmd = "cd "+workspace_path+" && "+command.entrypoint
            
            ret_code = subprocess.call(cmd, shell=True)
            if ret_code:
                print(ret_code)
                raise "Job failed"
            self.status = "FINISHED_AND_RUNNING"
            self.send_status_to_broker(self.status, command)

    def process(self, msg):
        self.commands = self._parse(msg)
        for command in self.commands:
            try:
                is_connected = self.check_connection(command)
                if is_connected:
                    if command.job_id not in self.command_list.keys():
                        self.command_list[command.job_id] = command
                        self._exec(command)
                    elif command.job_id:
                        tmp = self.status
                        self.status = "FINISHED_AND_RUNNING"
                        self.send_status_to_broker(self.status, command)
                        self.status = tmp
            except Exception as e:
                self.status = "JOB_FAILED"
                self.send_status_to_broker(self.status, command, str(e))

            if command.info not in ["ping"]:
                if (self.status not in ["NOT_CONNECTED"]):
                    self.send_finish_until_response(command)

    # TODO: write it as a thread
    def send_finish_until_response(self, command, threshold=3):

        def query():
            while True:
                self.status = "FINISHED"
                self.send_status_to_broker(self.status, command)
                time.sleep(threshold)

        if self.query_proc is None:
            self.query_proc = Process(target=query)
            self.query_proc.start()

        if(command.info=='ok'):
            self.query_proc.terminate()
            self.query_proc = None
            self.status = "FREE"
            self.send_status_to_broker(self.status, command)

    def check_connection(self, command):
        if command.info=='ping':
            self.connected = True
            self.id = self.instance_id
            self.status = "FREE"
            self.send_status_to_broker(self.status, command)
            return False
        elif self.connected==True:
            return True
        else:
            self.connected = False
            self.status = "NOT_CONNECTED"
            self.send_status_to_broker(self.status, command)
            return False
    
    def send_status_to_broker(self, status, command, note=None):
        if (status!=self.status):
            raise "错误：发送状态与本身状态不一致！"
        if command is None:
            message = {
                "status": self.status,
                "job_id": None,
                "instance_id": self.instance_id,
                "note": note
            }
        else:
            message = {
                "status": self.status,
                "job_id": command.job_id,
                "instance_id": self.instance_id,
                "note": note,
            }

        write_path = '/tmp/status_out'
        # set job configeration
        if not os.path.exists(write_path):
            raise "Please start your producer service first"
        print(type(message), message)
        message = json.dumps(message)
        message += '\n'

        # set job
        try:
            f = os.open(write_path, os.O_WRONLY)
            os.write(f, message.encode())
            os.close(f)
        except Exception as e:
            print(e)
            os.close(f)



class Command:
    def __init__(self, command_str, info=None):
        self.command = self._get_command_info(command_str)
        if info is not None:
            self.command = info

    def _get_command_info(self, info_str):
        try:
            info = json.loads(info_str)
        except:
            info = None
        return info

    @property
    def instance_id(self):
        return self.command['instance_id']

    @property
    # ping or NULL
    def info(self):
        return self.command['info']

    @property
    def git_url(self):
        return self.command['git_url']

    @property
    def username(self):
        return self.command['username']

    @property
    def project_name(self):
        return self.command['project_name']

    @property
    def entrypoint(self):
        return self.command['entrypoint']

    @property
    def job_id(self):
        return self.command['job_id']
    
    @property
    def log(self):
        try:
            return self.command['log']
        except:
            return None

    @property
    def output(self):
        try:
            return self.command['output']
        except:
            return None