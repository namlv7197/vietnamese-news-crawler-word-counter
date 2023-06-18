from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
import json
import os

try:
    import underthesea
except:
    os.system('python3 -m pip install underthesea')
    import underthesea

from underthesea import sent_tokenize,pos_tag

@F.udf(returnType=MapType(StringType(),StringType()))
def to_dict(text):
    return json.loads(text)

@F.udf(returnType=ArrayType(StringType()))
def tokenize(sentence):
    words=[word[0].lower() for word in pos_tag(sentence) if word[1]!='CH']
    return words

@F.udf(returnType=StringType())
def to_string(object_):
    return json.dumps(object_)

struct_schema = StructType([
    StructField('token', StringType(), nullable=True),
    StructField('frequency', StringType(), nullable=True)
])
@F.udf(returnType=struct_schema)
def create_struct(col1,col2):
    return {
        'token':col1,
        'frequency':col2
    }

struct_schema1 = StructType([
    StructField('news_id', StringType(), nullable=True),
    StructField('tokens', StringType(), nullable=True)
])

@F.udf(returnType=struct_schema1)
def map_concat_with_nested_map(col1,col2):
    return {
        'news_id':col1['news_id'],
        'tokens':col2['tokens']
    }


if __name__=='__main__':
    spark = SparkSession \
        .builder \
        .appName("test") \
        .getOrCreate()


    df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "54.179.7.184:9092,54.151.183.113:9092,54.254.228.131:9092") \
    .option("subscribe", "bao_tuoi_tre_topic") \
    .option("startingOffsets","latest") \
    .option("startingOffsetsByTimestampStrategy",'latest') \
    .option("startingTimestamp","1000") \
    .load()
    
    df=df.select('value',F.decode('value',charset='UTF-8').alias('example'))    
    
    df=df.select(to_dict('example').alias('example'))
    df=df.withColumn('news_id',df['example']['news_id'])
    df=df.withColumn('content',df['example']['content'])
    df=df.withColumn('tokens',tokenize('content'))
    df=df.withColumn('token',F.explode('tokens'))
    df=df.groupBy(['news_id','token']).count()
    df=df.withColumnRenamed('count','frequency')

    df=df.withColumn('value',create_struct('token','frequency'))
    df=df.groupBy('news_id').agg(F.collect_list('value').alias('value'))
    df=df.withColumn('value',F.map_from_entries('value'))
    df=df.withColumn('value',F.create_map(F.lit('tokens'),'value'))
    df=df.withColumn('news_id',F.create_map(F.lit('news_id'),'news_id'))
    df=df.withColumn('value',map_concat_with_nested_map('news_id','value'))

    df=df.withColumn('value',to_string('value'))
    df=df.withColumn('value',F.encode('value',charset='UTF-8'))

    df.writeStream \
    .format('kafka') \
    .trigger(processingTime='2 seconds') \
    .outputMode('update') \
    .option("checkpointLocation","file:///home/lvnam7197/Documents/kafka/ckpt_dir") \
    .option("kafka.bootstrap.servers", "54.179.7.184:9092,54.151.183.113:9092,54.254.228.131:9092") \
    .option("topic", "bao_tuoi_tre_word_counter") \
    .start() \
    .awaitTermination()