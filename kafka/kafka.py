from confluent_kafka import Consumer, Producer, KafkaError
from app.model import detect_anomalies

import json
import yaml

with open("../kafka/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Kafka Producer 설정
producer_conf = {
    'bootstrap.servers': config['kafka']['bootstrap_servers'],
    'client.id': config['kafka']['producer']['client_id']
}
producer = Producer(producer_conf)

consumer_conf = {
    'bootstrap.servers': config['kafka']['bootstrap_servers'],
    'group.id': config['kafka']['consumer']['group_id'],
    'auto.offset.reset': config['kafka']['consumer']['auto_offset_reset'],
    'session.timeout.ms': config['kafka']['consumer']['session_timeout_ms'],
    'heartbeat.interval.ms': config['kafka']['consumer']['heartbeat_interval_ms'],
    'max.poll.interval.ms': config['kafka']['consumer']['max_poll_interval_ms']
}
consumer = Consumer(consumer_conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def process_messages():
    consumer.subscribe([config['kafka']['topics']['input_topic']])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)  # 메시지 대기
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError.PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            # 받은 메시지를 JSON으로 변환
            span_event = json.loads(msg.value().decode('utf-8'))
            print(f"Received SpanCollectedEvent: {span_event}")

            # 스팬 리스트에서 이상치 탐지
            anomalies = detect_anomalies(span_event)

            trace_id = anomalies["traceId"]

            serialized_key = str(trace_id).encode('utf-8')
            serialized_value = json.dumps(anomalies).encode('utf-8')

            # Kafka에 메시지 전송
            producer.produce(
                topic=config['kafka']['topics']['output_topic'],
                key=serialized_key,
                value=serialized_value,
                callback=delivery_report
            )

            producer.flush()

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        producer.flush()
