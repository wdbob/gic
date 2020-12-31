FROM wangziling100/kafka:broker

ENV KAFKA_BROKER_CONFIG="/usr/kafka_broker/config/server.properties" \
    ZOOKEEPER_SERVER="localhost:2181" \
    EXTIP="localhost" \
    INTIP="localhost"
COPY kafka_broker.sh /usr/
EXPOSE 9092
CMD ["bin/bash", "/usr/kafka_broker.sh"]