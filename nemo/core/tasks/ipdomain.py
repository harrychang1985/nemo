#!/usr/bin/env python3
# coding:utf-8
import re
import requests
import dns.resolver
from .taskbase import TaskBase
from nemo.core.database.ip import Ip
from nemo.core.database.domain import Domain
from nemo.common.utils.iputils import check_ip_or_domain


class IpDomain(TaskBase):
    '''IP归属地、域名解析的任务
    参数：options
            {
                'target':['ip'/'domain',...]#ip或者domain列表
            }
    任务结果：
        保存为ip或domain资产的格式
        [{'ip': '218.19.148.193', 'location': 'xxx'}, {'ip': '121.8.169.18', 'location': 'xxx'}, 
        {'domain': 'www.sgcc.com.cn', 'CNAME': [], 'A': ['210.77.176.16']}, 
        {'domain': '95598.gd.csg.cn', 'CNAME': [], 'A': ['121.8.169.18']}]
    '''
    def __init__(self):
        super().__init__()
        self.task_name = 'ipdomain'
        self.task_description = 'ip 归属地查询、域名解析'
        self.source = 'portscan'

        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)'}
        self.timeout = 5

    def __fetch_iplocation_from_7188(self, ip):
        '''调用www.hao7188.com的接口查询指定的IP地址
        '''
        url = 'http://www.hao7188.com/'
        session = requests.Session()
        try:
            r1 = session.get(url, headers=self.headers)
            if r1.status_code == requests.codes.ok:
                pattern = r'name="so_token" value="(.*?)">'
                m = re.findall(pattern, r1.text)
                token = m[0] if m and len(m) > 0 else ''
                if token != '':
                    url = 'http://www.hao7188.com/query.html?ip={}&so_token={}'.format(
                        ip, token)
                    r2 = session.get(url, headers=self.headers)
                    if r2.status_code == requests.codes.ok:
                        m = re.findall(
                            r"<script>window\.location\.href = '(.*?)'</script>", r2.text)
                        new_href = m[0] if m and len(m) > 0 else ''
                        if new_href != '':
                            url_new = 'http://www.hao7188.com/{}'.format(
                                new_href)
                            r3 = session.get(url_new, headers=self.headers)
                            p = u'<span>(.*?)</span>'
                            m = re.findall(p, r3.text)
                            return m
        except:
            pass

        return None

    def __fetch_iplocation_from_ipcn(self, ip):
        '''调用ip.cn查询IP地址
        '''
        url = 'https://ip.cn?ip={}'.format(ip)

        try:
            r = requests.get(url, headers=self.headers, timeout=self.timeout)
            if r.status_code == requests.codes.ok:
                p = r'<code>(.*?)</code>'
                m = re.findall(p, r.text)
                return m
        except:
            pass

        return None


    def fetch_domain_ip(self, domain):
        '''查询域名对应的IP，返回结果A是域名对应的IP地址
        如果返回结果包含了CNAME（域名的别名），返回的地址可能是CDN的地址
        '''
        iplist = {'domain':domain,'CNAME': [], 'A': []}
        try:
            A = dns.resolver.query(domain, 'A')
            for i in A.response.answer:
                for j in i.items:
                    if j.rdtype == 5:
                        iplist['CNAME'].append(j.to_text())
                    elif j.rdtype == 1:
                        iplist['A'].append(j.address)
        except Exception as e:
            pass

        return iplist

    def __fetch_same_domain(self, ip):
        '''调用chinaz查询同IP的域名
        '''
        url = 'http://s.tool.chinaz.com/same?s={}'.format(ip)
        try:
            r = requests.get(url, headers=self.headers, timeout=self.timeout)
            if r.status_code == requests.codes.ok:
                p = r'target=_blank>(.*?)</a>'
                m = re.findall(p, r.text)
                return m
        except:
            pass

        return []

    def prepare(self, options):
        '''解析参数
        '''
        self.org_id = self.get_option('org_id',options,self.org_id)
        for host in options['target']:
            if check_ip_or_domain(host):
                self.target.append({'ip': host})
            else:
                self.target.append({'domain': host})

    def execute_iplocation(self, ips):
        '''查询IP归属地
        '''
        for ip in ips:
            if 'ip' not in ip:
                continue
            ip_loc = self.__fetch_iplocation_from_7188(ip['ip'])
            if ip_loc and len(ip_loc) > 0:
                ip['location'] = ','.join(ip_loc)
                continue
            ip_loc = self.__fetch_iplocation_from_ipcn(ip['ip'])
            if ip_loc and len(ip_loc) >= 2:
                ip['location'] = ip_loc[1]

        return ips

    def execute_domainip(self, domains):
        '''查询domain对应的IP
        '''
        for domain in domains:
            if 'domain' not in domain:
                continue
            domain.update(self.fetch_domain_ip(domain['domain']))

        return domains

    def save_ip(self, data):
        '''保存IP归属地结果到数据库
        只更新ip表的location字段
        '''
        ip_app = Ip()
        count = 0
        for ip in data:
            if 'location' in ip and ip['location']:
                if self.org_id:
                    ip['org_id'] = self.org_id
                count += 1 if ip_app.save_and_update(ip) > 0 else 0

        return count

    def run_iplocation(self, options):
        '''根据IP获得归属地
        '''
        self.prepare(options)
        self.execute_iplocation(self.target)
        result={'status': 'success',
                  'count': self.save_ip(self.target)}

        return result

    def run_domainip(self, options):
        '''给定域名，查询对应的IP地址
        '''
        self.prepare(options)
        self.execute_domainip(self.target)
        result = self.save_domain(self.target)
        result['status'] = 'success'

        return result
