import base64
import json
import logging

import os

job_file_path = "/seatunnel/job/application.conf"
hive_file_path = "/spark/conf/hive-site.xml"
logging.getLogger().setLevel(logging.INFO)

# 保存seatunnel配置文件
def save_job_conf(render_str):
    """
    :desc save code as a conf script
    :param render_str: pure code
    :return: save_ret: 0 save failed, else 1
    """

    save_ret = 1
    render_dict = json.loads(render_str)
    if render_dict.get('seatunnel_conf'):
        try:
            with open(job_file_path, "w+", encoding='utf-8') as f:
                f.write(str(render_dict.get('seatunnel_conf').strip()))
        except Exception as exp:
            save_ret = 0
            logging.error("save conf file failed, exp: {}".format(exp), exc_info=True)
        finally:
            f.close()
    else:
        save_ret = 0
        logging.error("get param seatunnel_conf failed")
    return save_ret


# 保存hive xml配置文件
def save_hive_xml(render_str):
    """
    :desc save code as a xml script
    :param render_str: pure code
    """

    render_dict = json.loads(render_str)
    if render_dict.get('hive_conf'):
        try:
            with open(hive_file_path, "w+", encoding='utf-8') as f:
                f.write(str(render_dict.get('hive_conf').strip()))
        except Exception as exp:
            logging.error("save xml file failed, exp: {}".format(exp), exc_info=True)
        finally:
            f.close()


# 获取环境变量参数
def get_params():
    try:
        operator_params = os.environ.get('operator_params')
        render_str = base64.b64decode(operator_params).decode(encoding='utf-8')
        logging.info(f'-------------------- render_str: {render_str} --------------------')
        return render_str, None
    except Exception as error:
        return None, error


def main():
    # 获取环境变量参数
    render_str, error = get_params()
    if not render_str:
        logging.error('获取 operator_params 失败')
        return

    # 保存seatunnel配置文件
    job_save_ret = save_job_conf(render_str)

    # 保存hive xml配置文件
    save_hive_xml(render_str)

    # 执行seatunnel
    if not job_save_ret: return
    command = f"/seatunnel/bin/start-seatunnel-spark.sh --master local[4] --deploy-mode client --config {job_file_path}"
    result = os.system(command)
    if result != 0 and result != "0":
        logging.info(f'-------------------- command_failed_code: {result}  --------------------')
        raise IOError
    else:
        logging.info(f'-------------------- command_succeed_code: {result} --------------------')


if __name__ == '__main__':
    main()
