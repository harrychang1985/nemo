#!/usr/bin/env python3
# coding:utf-8
import traceback
from multiprocessing.dummy import Pool

from nemo.common.utils.iputils import check_ip_or_domain
from nemo.common.utils.loggerutils import logger
from nemo.core.tasks.taskbase import TaskBase


class PortFingerBase(TaskBase):
    '''获取端口指纹的基础类
    参数:options  
            {   
                'target':   [url1,url2,ur3...],url列表可是以doamin或IP:PORT，如www.google.com 或 8.8.8.8:80
                'org_id':   id,target关联的组织机构ID
            }
    任务结果:
        保存为ip或domain资产格式的列表：
        [{'port':'192.168.1.1','port':[{'port':80,'httpx':'xxx,yyy,zzz','source':'httpx'},...]},...]
        [{'domain':'www.google.com,'httpx':['xxx',]},...]
    '''

    def __init__(self):
        super().__init__()

        # 任务名称
        self.task_name = 'portfinger'
        # 任务描述
        self.task_description = '获取端口指纹'
        # 参数
        self.org_id = None
        self.source = 'portfinger'
        self.result_attr_keys = ('title', 'server')
        self.threads = 5
        # 默认的参数
        self.target = []
        # 设置port黑名单，避免无意义的浪费时间和资源
        # 根据使用的结果统计的top-ports （包括custome）
        # 7,9,13,17,19,21,22,23,25,53,79,80,81,85,88,100,106,110,111,113,119,143,144,179,199,389,427,
        # 443,444,514,515,543,554,631,636,646,880,902,990,993,1000,1010,1025,1026,1027,1028,1029,1030,1054,1055,1080,
        # 1111,1296,1322,1433,1556,1688,1723,1801,1900,1935,1947,2000,2001,2020,2049,2103,2105,2107,2121,2179,2200,2222,
        # 2383,2869,3000,3128,3300,3301,3306,3476,4001,4242,5000,5003,5051,5060,5357,5432,5555,5800,5900,5989,
        # 6000,6001,6006,6379,6543,6565,6667,6668,7000,7001,7002,7070,7443,7777,7778,7921,
        # 8000,8008,8009,8010,8031,8042,8080,8081,8083,8084,8085,8086,8087,8088,8099,8100,8181,8291,8300,8443,8800,8888,
        # 9001,9009,9010,9081,9090,9100,9878,9999,10000,10001,10002,10003,10004,10009,10012,10022,11111,11433,11521,12345,
        # 13306,13307,13314,13315,13389,13782,14000,15432,15900,15901,16379,17001,17002,17003,17004,17005,17006,17007,17008,17009,17010,
        # 18080,18081,18082,18083,18084,18085,18086,18087,18088,18089,19000,19001,19002,19003,19007,19008,19009,
        # 19100,19101,19102,19103,19104,19108,19200,19207,19315,20000,20020,20021,20162,37017,37021,37024,
        # 49152,49153,49154,49155,49156,49157,49158,49159,49160,49161,49163,49165,49167,49175,49176,50000,50500
        self.black_port = [7, 9, 13, 17, 19, 21, 22, 23, 25, 26, 37, 53, 100, 106, 110, 111, 113, 119, 135, 138, 139,
                           143, 144, 145, 161,
                           179, 199, 389, 427, 444, 445, 514, 515, 543, 554, 631, 636, 646, 880, 902, 990, 993,
                           1433, 1521, 3306, 5432, 3389, 5900, 5901, 5902, 49152, 49153, 49154, 49155, 49156, 49157,
                           49158, 49159, 49160, 49161, 49163, 49165, 49167, 49175, 49176,
                           13306, 11521, 15432, 11433, 13389, 15900, 15901]

    def fetch_title(self, url):
        '''获取一个URL的标题
        由继承类实现
        '''

    def prepare(self, options):
        '''解析参数
        '''
        # 将 [url1,url2,ur3...]格式处理为ip和domain表的格式
        target_list = []
        for t in options['target']:
            u = t.split(':')
            port = u[1] if len(u) == 2 else 80
            # IP地址
            if check_ip_or_domain(u[0]):
                for i in target_list:
                    if 'port' in i and 'port' in i and i['port'] == u[0]:
                        i['port'].append({'port': port})
                        break
                else:
                    target_list.append({'port': u[0], 'port': [{'port': port}]})
            else:
                # 域名
                for d in target_list:
                    if 'domain' in d and d['domain'] == t:
                        break
                else:
                    target_list.append({'domain': t})

        self.target = target_list
        self.org_id = self.get_option('org_id', options, self.org_id)

    def execute_worker(self, target):
        '''ip参数执行线程
        '''
        # IP:PORT
        if 'ip' in target and 'port' in target:
            for port in target['port']:
                if int(port['port']) in self.black_port:
                    continue
                if int(port['port']) in [443, 8443]:
                    url = 'https://{}:{}'.format(target['ip'], port['port'])
                else:
                    url = '{}:{}'.format(target['ip'], port['port'])
                content = self.fetch_title(url)
                if content:
                    port.update(self.parse_result(content))

        # DOMAIN
        elif 'domain' in target:
            content = self.fetch_title('{}'.format(target['domain']))
            if content:
                result = self.parse_result(content)
                if 'title' in result:
                    if 'title' not in target:
                        target['title'] = []
                    target['title'].append(result['title'])
                if 'server' in result:
                    if 'server' not in target:
                        target['server'] = []
                    target['server'].append(result['server'])
                if self.source in result:
                    target[self.source] = []
                    target[self.source].append(result[self.source])

    def parse_result(self, content):
        '''从返回中提取title和banner
        由继承类实现
        '''

    def execute(self, target_list):
        '''调用httpx执行扫描任务
        '''
        pool = Pool(self.threads)
        pool.map(self.execute_worker, target_list)
        pool.close()
        pool.join()

        return target_list

    def run(self, options):
        '''执行任务
        '''
        try:
            self.prepare(options)
            self.execute(self.target)
            result = self.save_ip(self.target)
            result.update(self.save_domain(self.target))
            result['status'] = 'success'

            return result
        except Exception as e:
            logger.error(traceback.format_exc())
            return {'status': 'fail', 'msg': str(e)}
