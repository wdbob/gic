#!/usr/bin/python  
# -*- coding: utf-8 -*

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models
import json


class InstanceController:
    def __init__(self, secret, key, instance):
        self.instance = instance
        self.status = "UNKNOWN"
        try:
            cred = credential.Credential(secret, key) 
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cvm.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = cvm_client.CvmClient(cred, "ap-shanghai", clientProfile)
            self.client = client
        except TencentCloudSDKException as err:
            print(err)
        

    def start(self):
        if self.client and self.status!='PENDING' and self.status!='RUNNING':
            try: 
                req = models.StartInstancesRequest()
                params = {
                    "InstanceIds": [self.instance]
                }
                req.from_json_string(json.dumps(params))

                resp = self.client.StartInstances(req) 
                #print(resp.to_json_string()) 

            except TencentCloudSDKException as err: 
                print(err)
        else:
            print('请重新实例化InstanceController!')


    def stop(self):
        if self.client and self.status!='PENDING' and self.status!='STOPPED':
            try: 
                req = models.StopInstancesRequest()
                params = {
                    "InstanceIds": [self.instance],
                    "StoppedMode": "STOP_CHARGING"
                }
                req.from_json_string(json.dumps(params))
                resp = self.client.StopInstances(req) 
                print(resp.to_json_string()) 

            except TencentCloudSDKException as err: 
                print(err)
        else:
            print('请重新实例化InstanceController!')

    def is_alive(self, ins):
        pass

    def get_status(self):
        self.check_status()
        return self.status

    def check_status(self):
        if self.client:
            try:
                req = models.DescribeInstancesStatusRequest()
                params = {
                    "InstanceIds": [ self.instance ]
                }
                req.from_json_string(json.dumps(params))

                resp = self.client.DescribeInstancesStatus(req) 
                # print(resp.to_json_string()) 
                info = json.loads(resp.to_json_string())
                self.status = info["InstanceStatusSet"][0]["InstanceState"]
                print(self.status)

            except TencentCloudSDKException as err: 
                self.status = "UNKNOWN"
                print(err) 
        else:
            self.status = "UNKNOWN"
            print('请重新实例化InstanceController!')

if __name__ == "__main__":
    with open('config.json', 'r') as f:
        params = json.load(f)
    ic = InstanceController(params['id'], params['key'], params['instance'])
    ic.stop()
    ic.check_status()