# vietnamese-news-crawler-word-counter

Word counter in the news content by Spark Standalone

Author: Le Viet Nam

## Install Java 8
```
sudo apt-get update
sudo apt install openjdk-8-jdk -y
```

## Download and extract Spark
Assumption working directory is ```/home/ubuntu```
```
cd /home/ubuntu
wget https://dlcdn.apache.org/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz
tar -xvf spark-3.4.0-bin-hadoop3.tgz
mv spark-3.4.0-bin-hadoop3 spark
```
## Configure Spark
Assumption Private IP: 192.168.0.11
Modify conf/spark-env.sh by inserting these following lines
```
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export SPARK_HOME=/home/ubuntu/spark
export SPARK_MASTER_HOST=192.168.0.11
export SPARK_MASTER_PORT=7000
export SPARK_MASTER_WEBUI_PORT=8000
export SPARK_CONF_DIR=${SPARK_HOME}/conf
```

Modify conf/spark-defaults.conf by inserting these following lines
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
## Start Spark master
```
cd /home/ubuntu/spark
./sbin/start-master.sh
```

## Start Spark Workernode
```
./sbin/start-worker.sh spark://192.168.0.11:7000
```

## Clone git repository
```
git clone vietnamese-news-crawler-word-counter
./bin/spark-submit --master spark://master:7000 --deploy-mode client --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0 --conf spark.app.name=word_counter vietnamese-news-crawler-word-counter/word_counter.py


```


