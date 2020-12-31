import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models

with open('config.json', 'r') as f:
        params = json.load(f)
try: 
    cred = credential.Credential(params['id'], params['key']) 
    httpProfile = HttpProfile()
    httpProfile.endpoint = "cvm.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = cvm_client.CvmClient(cred, "ap-shanghai", clientProfile) 

    req = models.StartInstancesRequest()
    params = {
        "InstanceIds": [ "ins-1z5cejjd" ]
    }
    req.from_json_string(json.dumps(params))

    resp = client.StartInstances(req) 
    print(resp.to_json_string()) 

except TencentCloudSDKException as err: 
    print(err) 