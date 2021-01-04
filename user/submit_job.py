#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import os
from argparse import ArgumentParser


def run():
    write_path = '/tmp/jobs_out'
    # set job configeration
    if not os.path.exists(write_path):
        raise "Please start your producer service first"
    argv = ArgumentParser(usage='submit_job [-f job配置文件]', description='提交任务工具')
    argv.add_argument('-f', default=os.path.join(os.path.dirname(__file__), './job_format.json'), type=str, help='job配置文件')
    args = argv.parse_args()
    json_fn = args.f
    with open(json_fn, 'r') as f:
        params = json.load(f)
    message = json.dumps(params)

    # set job
    try:
        f = os.open(write_path, os.O_WRONLY)
        os.write(f, message)
        os.close(f)
    except:
        os.close(f)


if __name__ == "__main__":
    run()