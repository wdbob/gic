import os
import json

def send_ping_command():
    command = {
        "info": "ping",
        "git_url": None,
        "username": "wangxb",
        "project_name": "Hello-World",
        "entrypoint": "HelloWorld.py",
        "job_id": -1,
    }
    write_path = '/tmp/command_out'
    # set job configeration
    message = json.dumps(command)
    message += '\n'

    # set job
    try:
        f = os.open(write_path, os.O_WRONLY)
        os.write(f, message.encode())
        os.close(f)
    except Exception as e:
        print(e)
        os.close(f)

def send_hello_command():
    command = {
        "info": "command",
        "git_url": "git@github.com:blackbird71SR/Hello-World.git",
        "username": "wangxb",
        "project_name": "Hello-World",
        "entrypoint": "python3 HelloWorld.py",
        "job_id": -1,
    }
    write_path = '/tmp/command_out'
    # set job configeration
    message = json.dumps(command)
    message += '\n'

    # set job
    try:
        f = os.open(write_path, os.O_WRONLY)
        os.write(f, message.encode())
        os.close(f)
    except Exception as e:
        print(e)
        os.close(f)

if __name__ == "__main__":
    send_hello_command()