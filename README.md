# Nemo

<img src="docs/nemo.jpg" alt="nemo" align="left"/>

Nemo（尼莫）是《海底总动员》中的一只可爱的小丑鱼。

Nemo的初衷是用来进行自动化信息收集的一个简单平台，实现对内网及互联网资产信息的自动收集。

## 


## 功能

主要实现了以下功能（代码目前在完善和优化中...）

- 采用Nmap进行端口扫描（需本地安装好nmap）
- 端口标题查询
- 通过第三方接口查询IP归属地
- 调用Sublist3r实现子域名收集
- 调用Fofa的API接口对IP和域名信息收集（需要Fofa的KEY）
- 调用WhatWeb收集端口和域名的指纹（需本地安装好whatweb）
- Celery实现分布式任务





## Docker运行

```shell
docker build  -t nemo/app:v1 .
docker run -it -d --name nemo_app -p 5000:5000 nemo/app:v1
```

浏览器输入http://localhost:5000，默认用户名密码：nemo/nemo


<img src="docs/login.jpg" alt="login" style="zoom:50%;" />

<img src="docs/dashbord.jpg" alt="dashbord" style="zoom:50%;" />





## 手工配置（非docker环境）

### 0、分布式配置

1台主服务器+N台任务服务器

- **主服务器：（以IP为172.16.80.1为例）**

  组件：mysql + rabbitmq + celery + flower + web

- **任务服务器（能够访问主服务器的mysql和rabbitmq）**

  组件：celery

### **1、rabbitmq**

- 设置监听的IP地址（供worker远程访问），修改/usr/local/Cellar/rabbitmq/{VERSION}/sbin/rabbitmq-env，增加
  
   ```
   NODE_IP_ADDRESS= 172.16.80.1 (rabbitmq所在服务器地址，供celery远程连接，如果不需要分布式则不需要该配置)
   ```
- 增加rabbitmq用户和密码
   ```
   rabbitmqctl add_user nemo nemo2020
   rabbitmqctl set_permissions -p "/" nemo ".*" ".*" ".*"
   ```

### **2、mysql**

- mysql的bind-address（brew 安装默认是127.0.0.1，创建~/.my.cnf文件并设置bind-address；如果不需要分布式则不需要该配置）
   ```
   # Default Homebrew MySQL server config
  [mysqld]
  # Only allow connections from localhost
  # bind-address = 127.0.0.1
  bind-address = 172.16.80.1
  ```


- 创建数据库
   ```
   CREATE DATABASE `nemo` DEFAULT CHARACTER SET utf8mb4;
   ```
- 导入nemo.sql
   ```
   mysql -u root nemo < nemo.sql
   ```
- 创建用户并授权
   ```
   CREATE USER 'nemo'@'%' IDENTIFIED BY 'nemo2020';
   GRANT ALL PRIVILEGES ON nemo.* TO 'nemo'@'%';
   FLUSH PRIVILEGES;
   ```
### 3、instance/config.py

- mysql数据库、用户名和密码

  ```
   # database
      DB_HOST = '172.16.80.1'	#如果是非分布式任务则localhost即可
      DB_PORT = 3306
      DB_NAME = 'nemo'
      DB_USERNAME = 'nemo'
      DB_PASSWORD = 'nemo2020'
  ```

- rabbitmq的地址、用户名和密码

  ```
   # rabbitmq
      MQ_HOST = '172.16.80.1'		#如果是非分布式任务则localhost即可#
      MQ_PORT = 5672
      MQ_USERNAME = 'nemo'
      MQ_PASSWORD = 'nemo2020'
  ```

- flower的地址及端口

  ```
  # flower
   		FLOWER_BIND_ADDR = '127.0.0.1'
      FLWOER_PORT = 5555
  ```

### 4、python package

  ```
pip3 install -r requirements.txt
  ```



## 运行

**主服务器**

1. 启动mysql和rabbitmq

2. 启动celery worker

   ```bash
   export PYTHONOPTIMIZE=1
   celery -A nemo.core.tasks.tasks worker --loglevel info
   ```

3. 启动celery flower

   ```bash
   celery flower -A nemo.core.tasks.tasks --address=127.0.0.1 -port-5555
   ```

4. 启动web app

   ```
   python3 app.py
   ```

**分布式任务**

1. 启动celery worker

   ```bash
   export PYTHONOPTIMIZE=1
   celery -A nemo.core.tasks.tasks worker --loglevel info
   ```



## 目标

最终做成像FOFA一样的信息收集平台。



## 参考

jeffzh3ng：https://github.com/jeffzh3ng/fuxi

TideSec：https://github.com/TideSec/Mars