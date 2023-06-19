from confluent_kafka import Consumer
import json

c = Consumer({
    'bootstrap.servers': '54.179.7.184:9092,54.151.183.113:9092,54.254.228.131:9092',
    'group.id': 'bao_tuoi_tre_word_counter',
    'auto.offset.reset': 'latest'
})

c.subscribe(['bao_tuoi_tre_word_counter'])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue
    msg=msg.value().decode('utf-8')
    msg=json.loads(msg)
    print('Received message: {}'.format(msg))

c.close()
