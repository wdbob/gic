import subprocess


def run():
    cmd = "docker stop broker-consumer"
    subprocess.call(cmd, shell=True)
    cmd = "docker rm broker-consumer"
    subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    run()