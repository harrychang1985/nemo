## MacOS下安装

### **0、git clone**

  ```
git clone --recursive https://github.com/hanc00l/nemo
  ```

### **1、rabbitmq**

  ```
brew install rabbitmq
  ```

### **2、mysql**

```
brew install mysql@5.7
```


- 创建数据库

  ```
  brew services run mysql@5.7
  mysql -u root
  	>CREATE DATABASE `nemo` DEFAULT CHARACTER SET utf8mb4;
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

### 3、nmap&masscan

```
brew install nmap masscan
# 因为nmap、masscan的SYN扫描需要root权限，为避免使用sudo，设置root权限的suid
cd /usr/local/Cellar/nmap/7.80_1/bin
sudo chown root nmap
sudo chmod u+s nmap
cd /usr/local/Cellar/masscan/1.0.5/bin
sudo chown root masscan
sudo chmod u+s masscan
```

### 4、whatweb

```
git clone https://github.com/urbanadventurer/WhatWeb
cd WhatWeb
# whatwebf需要编译和安装ruby，通过make install自动安装相关的ruby依赖
make install
```

### 5、instance/config.py

- mysql数据库、用户名和密码

  ```
   # database
      DB_HOST = 'localhost'	
      DB_PORT = 3306
      DB_NAME = 'nemo'
      DB_USERNAME = 'nemo'
      DB_PASSWORD = 'nemo2020'
  ```

- rabbitmq的地址、用户名和密码

  ```
   # rabbitmq
      MQ_HOST = '127.0.0.1'		
      MQ_PORT = 5672
      MQ_USERNAME = 'guest'
      MQ_PASSWORD = 'guest'
  ```

- flower的地址及端口

  ```
  # flower
      FLOWER_BIND_ADDR = '127.0.0.1'
      FLOWER_PORT = 5555
      FLOWER_AUTH_USER = 'nemo'
      FLOWER_AUTH_PASSWORD = 'nemo'
  ```

### 6、python package

  ```
pip3 install -r requirements.txt

  ```

### 

## 运行

 ### 1.mysql和rabbitmq

   ```
   brew services run mysql@5.7
   brew services run rabbitmq
   ```

### 2. celery worker

   ```bash
   export PYTHONOPTIMIZE=1
   celery -A nemo.core.tasks.tasks worker --loglevel info -c 4
   ```

### 3. celery flower

   ```bash
   celery flower -A nemo.core.tasks.tasks --basic_auth=nemo:nemo --address=127.0.0.1 -port-5555
   ```

### 4. web app

   ```
   python3 app.py
   ```

