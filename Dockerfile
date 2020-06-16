FROM ubuntu:18.04

ENV LC_ALL C.UTF-8

# Init
RUN set -x \
    # You may need this if you're in Mainland China
    && sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    ###
    && apt-get update \
    && apt-get install -y python3.7 python3.7-dev python3-pip python3-setuptools \
    wget curl vim net-tools git unzip \
    mysql-server rabbitmq-server \
    nmap whatweb --fix-missing

RUN mkdir -p /opt/nemo
COPY . /opt/nemo

# pip package
RUN set -x \
    # You may need this if you're in Mainland China
    # && python3.7 -m pip config set global.index-url 'https://pypi.mirrors.ustc.edu.cn/simple/' \
    && python3.7 -m pip install -U pip -i https://pypi.mirrors.ustc.edu.cn/simple/ \
    && python3.7 -m pip install -r /opt/nemo/requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/ \
    && chmod +x /opt/nemo/start.sh

# init databse and rabbitmq
RUN set -x \
    && service mysql start && service rabbitmq-server start \
    && rabbitmqctl add_user nemo nemo2020 && rabbitmqctl set_permissions -p "/" nemo ".*" ".*" ".*" \
    && mysql -u root -e 'DROP DATABASE IF EXISTS `nemo`;CREATE DATABASE `nemo` DEFAULT CHARACTER SET utf8mb4;' \
    && mysql -u root -e 'CREATE USER `nemo`@`%` IDENTIFIED BY `nemo2020`;GRANT ALL PRIVILEGES ON nemo.* TO `nemo`@`%`;FLUSH PRIVILEGES;' \
    && mysql -u root nemo < /opt/nemo/nemo.sql

ENV PYTHONOPTIMIZE 1
WORKDIR /opt/nemo
ENTRYPOINT ["/opt/nemo/start.sh"]
EXPOSE 5000 5555
