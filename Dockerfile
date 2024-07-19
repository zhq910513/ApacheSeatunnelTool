FROM harbor.deepwisdomai.com/deepwisdom/apache-seatunnel-spark:latest

ADD ./ /seatunnel-code
WORKDIR /seatunnel-code

RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list &&  sed -i 's|security.debian.org/debian-security|mirrors.ustc.edu.cn/debian-security|g' /etc/apt/sources.list

RUN apt-get -y update && apt-get -y install python3 python3-pip vim wget

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN wget https://mirrors.cloud.tencent.com/apache/incubator/seatunnel/2.1.2/apache-seatunnel-incubating-2.1.2-bin.tar.gz && tar -zxvf apache-seatunnel-incubating-2.1.2-bin.tar.gz

RUN mv /seatunnel-code/apache-seatunnel-incubating-2.1.2/connectors /seatunnel/connectors

RUN mv /seatunnel-code/seatunnel-connector-spark-clickhouse-2.1.2.jar /seatunnel/connectors/spark

RUN mv /seatunnel-code/mysql-connector-java.jar /spark/jars
RUN mv /seatunnel-code/clickhouse-jdbc-0.2.6-shaded.jar /spark/jars

RUN chmod -R 755 /spark/jars

RUN rm -rf /seatunnel-code/apache-seatunnel-incubating-2.1.2 && rm -rf /seatunnel-code/apache-seatunnel-incubating-2.1.2-bin.tar.gz

RUN mkdir /seatunnel/job

ENTRYPOINT ["python","/seatunnel-code/seatunnel_operator_executor.py"]