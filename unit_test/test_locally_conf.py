import os

# https://seatunnel.incubator.apache.org/docs/2.1.2/intro/about

# 处理环境
# unset  HADOOP_HOME
# unset HADOOP_CONF_DIR
# export SPARK_HOME=/opt/spark

command = f"./bin/start-seatunnel-spark.sh --master local[4] --deploy-mode client --config ./job/application.conf"
result = os.system(command)
print(f'-------------------- command_code: {result} --------------------')
