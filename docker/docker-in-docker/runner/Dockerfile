FROM registry.cn-shanghai.aliyuncs.com/wangxb/dind-base 
COPY agent.py /usr/
COPY command_processor.py /usr/
COPY id_ed25519 /root/.ssh/
COPY id_ed25519.pub /root/.ssh/
COPY known_hosts /root/.ssh/
RUN chmod -R 700 /root
CMD ["python3", "/usr/agent.py"]
