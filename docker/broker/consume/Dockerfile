FROM wangziling100/kafka:consumer
RUN apk add --no-cache python3 && \
    pip3 --no-cache-dir install tencentcloud-sdk-python
ENV KAFKA_BROKER_SERVER="localhost:9092" \
    KAFKA_TOPICS="test" 
COPY run.py /usr/
COPY instance_controller.py /usr/
COPY job_processor.py /usr/
CMD ["python3", "/usr/run.py"]