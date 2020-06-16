### 任务

#### 一、主动端口扫描类：
1、port_scan_nmap


#### 二、域名扫描：domain_scan
1、domain_scan_subdomain
2、domain_scan_oneforall

#### 三、指纹识别类：web_finger
1、web_scan_whatweb
2、web_scan_owt (obtain web title)

#### 四、被动扫描接口类：api_scan
1、api_scan_fofa
2、api_scan_shodan

任务调用格式
kwargs:
    {
        task_name:任务名称，用于标识任务
        options:任务参数
        {
            target:[(ip1,ip2,ip3...)]
            port:   [(port1,port2,...)]
            其它参数
        }
    }

run_xxx(){
    prepare
    execute
    save
}

prepare：参数准备，格式化
execute_xxx：执行并返回中间结果
save：调用dao类，保存到数据库中


任务执行中间结果：
ip
[{'ip':ip,'ports':[{'port':port1,'service':xxx,'title':xxxx},...]},...]
domain
[{'domain':domain,'CNAME':[],'A':[]},...]
