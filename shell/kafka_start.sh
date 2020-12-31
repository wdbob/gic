status=$(docker ps | grep kafka | wc -l)
if [[ $status -eq 0 ]];then
    echo 'Start Service...'
    docker run --name broker -p 9092:9092 -e EXTIP=118.89.115.57 -e INTIP=10.105.42.229 --net host -e KAFKA_TOPICS='test-topic' registry.cn-shanghai.aliyuncs.com/wangxb/kafka-broker:v1  
    docker run -d --name kafka -p 9092:9092 -p 2181:2181 -e KAFKA_ADVERTISED_HOST_NAME=localhost -e KAFKA_CREATE_TOPICS="test-topic:1:1"  registry.cn-shanghai.aliyuncs.com/wangxb/kafka-broker:v0
    docker exec kafka bin/kafka-topics.sh --create --topic job --bootstrap-server localhost:9092
    docker exec kafka bin/kafka-topics.sh --create --topic instance-status --bootstrap-server localhost:9092
fi