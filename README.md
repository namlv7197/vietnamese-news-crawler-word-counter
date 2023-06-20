# vietnamese-news-crawler-word-counter

Count word frequency of news content by Spark Standalone.

Author: Le Viet Nam

## Install Java 8
```
sudo apt-get update
sudo apt install openjdk-8-jdk -y
```
## Install python virtual environment
```
sudo apt update && apt install -y python3-venv
```
## Create python virtual environment
```
mkdir python3_venvs
python3 -m venv python3_venvs/vietnamese-news-crawler-word-counter
source /home/ubuntu/python3_venvs/vietnamese-news-crawler-word-counter/bin/activate
```
## Download and extract Spark
Assumption working directory is ```/home/ubuntu```
```
cd /home/ubuntu
wget https://dlcdn.apache.org/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz
tar -xvf spark-3.4.0-bin-hadoop3.tgz
mv spark-3.4.0-bin-hadoop3 spark
cd spark/
```
## Configure Spark
Remove template suffix in ```conf/```
```
mv conf/spark-env.sh.template conf/spark-env.sh
mv conf/spark-defaults.conf.template conf/spark-defaults.conf
```
Modify ```conf/spark-env.sh``` by inserting these following lines (for master)
```
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export SPARK_HOME=/home/ubuntu/spark
export SPARK_MASTER_HOST=52.221.251.208
export SPARK_MASTER_PORT=7000
export SPARK_MASTER_WEBUI_PORT=8000
export SPARK_CONF_DIR=${SPARK_HOME}/conf
```

Modify ```conf/spark-defaults.conf``` by inserting these following lines (for worker/client)
```
spark.executor.cores=1
spark.executor.memory=512m
spark.dynamicAllocation.enabled=true
spark.dynamicAllocation.initialExecutors=1
spark.sql.streaming.statefulOperator.checkCorrectness.enabled=false
spark.sql.streaming.stateStore.stateSchemaCheck=false
spark.sql.mapKeyDedupPolicy=LAST_WIN
spark.dynamicAllocation.maxExecutors=1
```

## Start Spark Workernode
Master WebUI [Master](http://52.221.251.208:8000/)
```
./sbin/start-worker.sh spark://52.221.251.208:7000
```

## Clone git repository and install ```requirements```
```
git clone https://github.com/namlv7197/vietnamese-news-crawler-word-counter.git
pip install -r vietnamese-news-crawler-word-counter/requirements.txt
```

### Run Spark query streaming
Applications will use query streaming to listen kafka message from ```bao_tuoi_tre_topic``` topic and send the processed output to ```bao_tuoi_tre_word_counter``` topic.
```
./bin/spark-submit \
 --master spark://52.221.251.208:7000 \
 --deploy-mode client \
 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0 \
 --conf spark.app.name=word_counter \
 vietnamese-news-crawler-word-counter/word_counter.py
```

## Check message sent to Kafka topic
Copy the following content and run
```
from confluent_kafka import Consumer
import json

c = Consumer({
    'bootstrap.servers': '54.255.215.10:9092,13.212.251.13:9092,13.212.207.232:9092',
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
```
Or
```
source /home/ubuntu/python3_venvs/vietnamese-news-crawler-word-counter/bin/activate
python3 vietnamese-news-crawler-word-counter/listen_message.py
```

