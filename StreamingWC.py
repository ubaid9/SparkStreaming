from pyspark.sql import SparkSession
from pyspark.sql.functions import *

from lib.logger import Log4j

if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("Streaming Word Count") \
        .master("local[3]") \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.sql.shuffle.partitions", 3) \
        .getOrCreate()

    logger = Log4j(spark)
    # Step 1: Read a streaming source- Input DataFrame
    lines_df = spark.readStream \
        .format("socket") \
        .option("host", "localhost") \
        .option("port", "9999") \
        .load()

    lines_df.printSchema()

    # Step 2 : Transform - Output DataFrame
    words_df = lines_df.select(expr("explode(split(value,' ')) as word"))
    counts_df = words_df.groupBy("word").count()

    # Step 3: Write the output - Sink
    word_count_query = counts_df.writeStream \
        .format("console") \
        .outputMode("complete") \
        .option("checkpointLocation", "chk-point-dir") \
        .start()

    logger.info("Listening to localhost:9999")
    word_count_query.awaitTermination()
