import base64
import json
import logging
import os
import time
import unittest
import warnings
from subprocess import PIPE, run

logging.getLogger().setLevel(logging.INFO)


class Test(unittest.TestCase):
    def setUp(self):
        self.operator_params = None
        self.docker_name = None
        self.init_data()

    def tearDown(self):
        self.delete_container()

    @classmethod
    def setUpClass(cls) -> None:
        warnings.simplefilter('ignore', ResourceWarning)

    @staticmethod
    def import_env_data():
        seatunnel_conf = """
env {
  spark.streaming.batchDuration = 5
  spark.app.name = "seatunnel"
  spark.ui.port = 13000
  spark.sql.catalogImplementation = "hive"
}

source {
  jdbc {
    driver = "com.mysql.cj.jdbc.Driver",
    url = "jdbc:mysql://192.168.50.22:13306/seatunnel_test",
    user = "root"
    password = "dataset_admin"
    table = "test"
    result_table_name = "test_mysql_to_hive"
  }
}

transform {
}

sink {
  Hive {
    source_table_name = "test_mysql_to_hive"
    result_table_name = "test_mysql_to_hive"
    save_mode = "overwrite"
  }
}
        """
        hive_conf = """
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<!--property>

<name>hive.server2.authentication</name>

<value>NOSASL</value>

</property-->
  <property>
    <name>spark.yarn.jars</name>
    <!--<value>hdfs://hadoop1:9820/spark2-jars/*</value>-->
    <value>${fs.defaultFS}/spark2-jars/*</value>
  </property>

  <!-- Hive3 执行引擎设为spark -->
  <property>
    <name>hive.execution.engine</name>
    <value>mr</value>
  </property>
  <!-- Hive3 和Spark2 连接超时时间 -->
  <property>
    <name>hive.spark.client.connect.timeout</name>
    <value>400000ms</value>
  </property>

    <property>
        <name>javax.jdo.option.ConnectionURL</name>
        <value>jdbc:mysql://hadoop2:3306/metastore?useSSL=false</value>
    </property>

    <property>
        <name>javax.jdo.option.ConnectionDriverName</name>
        <value>com.mysql.jdbc.Driver</value>
    </property>

    <property>
        <name>javax.jdo.option.ConnectionUserName</name>
        <value>root</value>
    </property>

    <property>
        <name>javax.jdo.option.ConnectionPassword</name>
        <value>dw.147258</value>
    </property>

    <property>
        <name>hive.metastore.warehouse.dir</name>
        <value>/user/hive/warehouse</value>
    </property>

    <property>
        <name>hive.server2.logging.operation.enabled</name>
        <value>false</value>
        <description>When true, HS2 will save operation logs and make them available for clients</description>
    </property>

    <property>
        <name>hive.metastore.schema.verification</name>
        <value>false</value>
    </property>

    <property>
        <name>hive.metastore.uris</name>
        <value>thrift://hadoop2:9083</value>
    </property>

    <property>
    <name>hive.server2.thrift.port</name>
    <value>10000</value>
    </property>

    <property>
        <name>hive.server2.thrift.bind.host</name>
        <value>hadoop2</value>
    </property>

    <property>
        <name>hive.metastore.event.db.notification.api.auth</name>
        <value>false</value>
    </property>



  <property>
<name>hive.support.concurrency</name>
<value>true</value>
</property>
<property>
<name>hive.exec.dynamic.partition.mode</name>
<value>nonstrict</value>
</property>
<property>
<name>hive.exec.dynamic.partition</name>
<value>true</value>
</property>
<property>
<name>hive.exec.max.dynamic.partitions.pernode</name>
<value>1000</value>
</property>
<property>
<name>hive.exec.max.dynamic.partitions</name>
<value>10000</value>
</property>
<property>
<name>hive.txn.manager</name>
<value>org.apache.hadoop.hive.ql.lockmgr.DbTxnManager</value>
</property>
<property>
<name>hive.compactor.initiator.on</name>
<value>true</value>
</property>
<property>
<name>hive.compactor.worker.threads</name>
<value>1</value>
</property>
<property>
<name>hive.enforce.bucketing</name>
<value>true</value>
</property>
  <property>
    <name>spark.executor.memory</name>
    <value>2048m</value>
  </property>
  <property>
    <name>spark.executor.cores</name>
    <value>2</value>
  </property>
</configuration>
        """
        return seatunnel_conf, hive_conf

    def encode_data(self):
        seatunnel_conf, hive_conf = self.import_env_data()
        test_data = {'seatunnel_conf': seatunnel_conf, 'hive_conf': hive_conf}
        base64_data = base64.b64encode(bytes(json.dumps(test_data).encode('utf-8')))
        return base64_data

    def init_data(self):
        data = str(self.encode_data(), encoding="utf-8")

        os.environ['operator_params'] = data
        os.putenv('operator_params', data)
        os.environ.setdefault('operator_params', data)

        self.operator_params = os.environ.get('operator_params')
        self.assertIsNotNone(self.operator_params, msg="环境变量添加失败")
        logging.info(f'------- 环境变量增加成功 -------{self.operator_params}')

    @staticmethod
    def execute(command):
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        return result

    def delete_container(self):
        # 释放容器
        status = 1
        while status:
            command_select = f"sudo docker ps -a |grep {self.docker_name}"
            if 'Exited' in str(self.execute(command_select)):
                command_d = f"sudo docker rm -f {self.docker_name}"
                self.execute(command_d)
                logging.info(f'------- 容器【{self.docker_name}】释放成功 -------')
                status = 0
            time.sleep(2)

    def test_run_container(self):
        self.docker_name = f"test-{hash(self.operator_params)}"
        logging.info(f'------- 容器【{self.docker_name}】即将运行 -------')
        command_create = f"sudo docker run -d -e operator_params='{self.operator_params}' --name {self.docker_name} harbor.deepwisdomai.com/deepwisdom/flow_seatunnel:1.4"
        self.execute(command_create)

        command_run = f"sudo docker start {self.docker_name}"
        self.execute(command_run)
        logging.info(f'------- 容器【{self.docker_name}】运行成功 -------')


if __name__ == '__main__':
    unittest.main()
