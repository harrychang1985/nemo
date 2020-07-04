#!/usr/bin/env python3
# coding: utf-8
import re
import ipaddress


def parse_ip(ip_or_ips):
    '''解析IP或IP段
    支持三种方式:单个IP、IP掩码和IP片段
    192.168.1.1
    192.168.1.0/24
    192.168.1.1-192.168.2.1
    '''
    # 单个IP
    p1 = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    m1 = re.match(p1, ip_or_ips)
    if m1:
        return ip_or_ips
    # 掩码
    p2 = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$'
    m2 = re.match(p2, ip_or_ips)
    if m2:
        try:
            return [str(i) for i in ipaddress.ip_network(ip_or_ips, strict=False)]
        except:
            return []
    # ip片断
    p3 = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\-\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    m3 = re.match(p3, ip_or_ips)
    if m3:
        try:
            ip_start, ip_end = ip_or_ips.split('-')
            ips = []
            for i in range(int(ipaddress.ip_address(ip_start)), int(ipaddress.ip_address(ip_end))+1):
                ips.append(str(ipaddress.ip_address(i)))
            return ips
        except:
            return []

    return None


def check_ip_or_domain(ip_or_domain):
    '''检测传递的参数是IP域名，如果是IP则返回True,域名返回False
    192.168.1.1
    192.168.1.0/24
    192.168.1.1-192.168.2.1
    '''
    p1 = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    p2 = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}[\/\-]{1}'
    m = re.match(p1, ip_or_domain) or re.match(p2, ip_or_domain)

    return True if m else False
