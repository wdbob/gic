import subprocess

def run():
    cmd = 'docker stop broker'
    #cmd = cmd.split(' ')
    subprocess.call(cmd, shell=True)
    cmd = 'docker rm broker'
    #cmd = cmd.split(' ')
    subprocess.call(cmd, shell=True)
    cmd = 'docker stop producer'
    subprocess.call(cmd, shell=True)
    cmd = 'docker rm producer'
    subprocess.call(cmd, shell=True)
    cmd = 'docker stop zoo'
    subprocess.call(cmd, shell=True)
    cmd = 'docker rm zoo'
    subprocess.call(cmd, shell=True)
    cmd = 'docker stop consumer'
    subprocess.call(cmd, shell=True)
    cmd = 'docker rm consumer'
    subprocess.call(cmd, shell=True)
    cmd = 'docker stop producer-command'
    subprocess.call(cmd, shell=True)
    cmd = 'docker rm producer-command'
    subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    run()