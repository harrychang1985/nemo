#!/bin/bash

#Tested on ubuntu18.04 LTS

#apt-get
sudo apt-get update && sudo apt-get install -y python3.7 python3.7-dev python3-pip python3-setuptools \
    wget curl vim net-tools git unzip \
    mysql-server rabbitmq-server \
    nmap whatweb masscan --fix-missing

# pip package
python3.7 -m pip install -U pip -i https://mirrors.aliyun.com/pypi/simple/ \
    && python3.7 -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ 

# third party
cd nemo/common/thirdparty/Sublist3r/ && python3.7 setup.py install && cd ../../../..

# init databse and rabbitmq
sudo service mysql start \
    && mysql -u root -e 'CREATE DATABASE `nemo` DEFAULT CHARACTER SET utf8mb4;' \
    && mysql -u root -e 'CREATE USER "nemo"@"%" IDENTIFIED BY "nemo2020";GRANT ALL PRIVILEGES ON nemo.* TO "nemo"@"%";FLUSH PRIVILEGES;' \
    && mysql -u root nemo < nemo.sql \
