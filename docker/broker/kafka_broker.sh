echo "listeners=PLAINTEXT://$INTIP" >> $KAFKA_BROKER_CONFIG
echo "advertised.listeners=PLAINTEXT://$EXTIP" >> $KAFKA_BROKER_CONFIG
sed -i "/zookeeper.connect/c\zookeeper.connect=$ZOOKEEPER_SERVER" $KAFKA_BROKER_CONFIG
/usr/kafka_broker/bin/kafka-server-start.sh $KAFKA_BROKER_CONFIG