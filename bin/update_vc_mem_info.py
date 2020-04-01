import pymysql
import subprocess
import logging.config
vc_user='administrator@peogoo-inc.com'
vc_pass='Cgf5zM@8DXxb'
vc_ip='10.1.1.108'
LOG_PATH='/tmp/a.log'
ip = ["10.1.1.101", "10.1.1.102", "10.1.1.103", "10.1.1.104", "10.1.1.106", "10.1.1.107"]

LOGGING_CONFIG={
    "version":1,
    "disable_existing_loggers":False,
    "formatters":{
        "simple":{
            "format":"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "filters": {},
    "handlers":{
        "console":{
            "class":"logging.StreamHandler",
            "level":"DEBUG",
            "formatter":"simple"
        },
        "file_handler":{
            "class":"logging.handlers.RotatingFileHandler",
            "level":"INFO",
            "formatter":"simple",
            "filename":LOG_PATH,
            "maxBytes":10485760,
            "backupCount":10,
            "encoding":"utf-8"
        }
    },
    "loggers":{
        "":{
            "level":"INFO",
            "handlers":["console","file_handler"],
            "propagate":True
        }
    }
}


def bash(cmd):
    obj=subprocess.Popen(cmd,shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout_res=obj.stdout.read()
    stderr_res=obj.stderr.read()
    return stdout_res,stderr_res

def to_dic(li):
    """
    li=['Name: jituan-daihouguanli-test-252',]
    :param li:
    :return:
    """
    new_dic = {}
    for i in li:
        if ':' in i:
            k, v = i.split(':', 1)
            new_dic[k.strip()] = v.strip()
    return new_dic

def my_logger():
    logging.config.dictConfig(LOGGING_CONFIG)
    logger=logging.getLogger(__name__)
    return logger
def get_mem_info(host_ip, vc_user='administrator@peogoo-inc.com',vc_pass='Cgf5zM@8DXxb',vc_ip='10.1.1.108'):
    logger = my_logger()
    cmd_get_host_info = 'govc host.info -u "%s":"%s"@"%s" -k -host.ip=%s' % (vc_user, vc_pass, vc_ip, host_ip)
    stdout, stderr = bash(cmd_get_host_info)
    if stdout:
        stdout_li = stdout.decode('utf-8').split("\n")
        stdout = to_dic(stdout_li)
        if stderr:
            logger.error('获取主机: %s 信息失败 %s' % (self.host_ip))
        Mem_totle = int(stdout.get("Memory").split("M")[0])
        Mem_userd = int(stdout.get("Memory usage").split()[0])
        Mem_free = Mem_totle - Mem_userd
        Mem_free_G = Mem_free // 1024
        print(Mem_free_G)
        return int(Mem_free_G)
    else:
        logger.error("无此主机")

def update_mem_info(mem_info, host_ip):
#def update_mem_info(table):
    conn = pymysql.connect(
        host='10.1.1.114',
        user='vm_api',
        database='vm_testdb',
        password='jeio324ds',
        port=23316
    )

    cursor = conn.cursor()
    sql = 'update physicalmachine set host_free_mem = "%s" where host_ip= "%s"' %(mem_info, host_ip)
#    sql = "select * from %s" %(table)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    vc_user='administrator@peogoo-inc.com'
    vc_pass='Cgf5zM@8DXxb'
    vc_ip='10.1.1.108'
    
    for host_ip in ip:   
        mem_info=get_mem_info(host_ip)
        update_mem_info(mem_info, host_ip)
