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

- 创建用户并授权

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
   celery -A nemo.core.tasks.tasks worker -c 2 --loglevel info
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
   celery -A nemo.core.tasks.tasks worker -c 2 --loglevel info
   ```

