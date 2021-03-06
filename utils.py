import requests
import subprocess
import logging.config
import settings
import json
import os
import re

def get_args(url):
    """
    get
    url='http://127.0.0.1:8000/api/v1/vmhost/?vm_audit=1&vm_installed=0'
    :param url:
    :return:
    """
    response=requests.get(url)
    return response.json()

def patch_installed(url):
    """
    patch {"vm_installed": 1}
    url='http://127.0.0.1:8000/api/v1/vmhost/2/'
    :return:
    """
    header={"Content-Type":"application/json; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
            }
    data={"vm_installed": 1}
    response=requests.patch(url,data=json.dumps(data),headers=header)
    return response.json()

def bash(cmd):
    obj=subprocess.Popen(cmd,shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout_res=obj.stdout.read()
    stderr_res=obj.stderr.read()
    return stdout_res,stderr_res

def to_dic(li):
    """
    li=['Name:                   jituan-daihouguanli-test-252',]
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
    logging.config.dictConfig(settings.LOGGING_CONFIG)
    logger=logging.getLogger(__name__)
    return logger

def judgment_on(ip):
    """
    判断开机成功并弹出cdrom
    :param ip:
    :return:
    """
    del_know='sed -i /%s/d /root/.ssh/known_hosts'%ip
    bash(del_know)
    start='sshpass -p "1234567" ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no root@%s "/usr/bin/eject"'%ip
    # 为了解决Warning
    bash(start)
    stdout,stderr=bash(start)
    logger=my_logger()
    if stderr:
        logger.info('%s 虚拟机启动检测中 %s'%(ip,stderr.decode('utf-8').strip()))
        return False
    return True

# 打包相关
def set_password(ip):
    ks_path=os.path.join(settings.ISO_ROOT, 'isolinux', 'ks.cfg')
    test=re.match(r'^172.20.*',ip)
    if test:
        passwd='\$1\$VSmile07\$QfNkkDW8w5oX1rnSj1ezc0'
    else:
        passwd='\$1\$VSmile07sdfadf.gs'
    set_passwd='sed -i "s/rootpw --iscrypted .*/rootpw --iscrypted %s/" %s'%(passwd,ks_path)
    stdout,stderr=bash(set_passwd)
    if stderr:
        raise Exception('设置ks.cfg文件中设置密码失败 %s'%stderr)
    return True

def set_hostname(ip, vm_name=settings.HOSTNAMEPRE):
    ks_path=os.path.join(settings.ISO_ROOT, 'isolinux', 'ks.cfg')
    v1,v2,v3,v4=ip.split('.')
    hostname=('-').join((vm_name,v2,v3,v4))
    set_name='sed -i "s/network --hostname=.*/network --hostname=%s/" %s'%(hostname,ks_path)
    stdout,stderr=bash(set_name)
    if stderr:
        raise Exception('设置ks.cfg文件中主机名失败%s'%stderr)
    return hostname

def set_netsh(ip,gateway):
    file_path=os.path.join(settings.ISO_ROOT, 'init', 'net.sh')
    with open(file_path,'w',encoding='utf-8')as f:
        f.write('echo -e "DEVICE=eth0\\nBOOTPROTO=static\\nONBOOT=yes\\nPREFIX=23\\nIPADDR=%s\\nGATEWAY=%s\\nDNS1=114.114.114.114\\n">/mnt/sysimage/etc/sysconfig/network-scripts/ifcfg-eth0'%(ip,gateway))

def set_discdrom(dc,vm_name):
    dis_path=os.path.join(settings.ISO_ROOT, 'init', 'clean.sh')
    set_discmd='sed -i "s#python3 /export/VMWare_Auto/vm_create/bin/discdrom.py .*#python3 /export/VMWare_Auto/vm_create/bin/discdrom.py  %s %s\\"#" %s'%(dc,vm_name,dis_path)
    stdout,stderr=bash(set_discmd)
    if stderr:
        raise Exception('设置clean.sh文件中断开cdrom失败%s'%stderr)

# if __name__ == '__main__':
#     res=get_args('http://127.0.0.1:8000/api/v1/vmhost/?vm_audit=1&vm_installed=0')
#     print(res)
    # res,err=bash("govc about")
    # res,err=bash('govc about -u "name":"pass"@"ip" -k')
    # print('out',res.decode('gbk'))
    # print(err.decode('gbk'))
    # res=patch_installed('http://127.0.0.1:8000/api/v1/vmhost/3/')
    # print(res.get("vm_installed"))
