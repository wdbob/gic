FROM wangziling100/kafka:consumer
RUN apk add --no-cache python3
ENV KAFKA_BROKER_SERVER="localhost:9092" \
    KAFKA_TOPICS="test" 
COPY run.py /usr/
#COPY command_processor.py /usr/
CMD ["python3", "/usr/run.py"]