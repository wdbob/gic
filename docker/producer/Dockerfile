FROM wangziling100/kafka:producer
RUN apk add --no-cache python3
ENV KAFKA_BROKER_SERVER="localhost:9092" \
    KAFKA_TOPICS="test" 
COPY run.py /usr/
CMD ["python3", "/usr/run.py"]