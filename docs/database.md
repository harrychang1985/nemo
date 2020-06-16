## database

### 1、organization（组织）
1、id
2、org_name，组织名称，多级组织格式为"xxx/xxx"
3、order，顺序号
4、status，组织状态
create_datetime
update_datetime


### 2、ip（ip表）
1、id
2、ip，IP地址
3、ip_int，IP地址的整数值，用于实现C段查询、范围查询
4、org_id，ip所属组织
5、location，ip归属地
6、status，IP状态
create_datetime
update_datetime



### 3、port（端口表）
1、id
2、ip_id，对应IP（资产表ID）
3、port，端口号
6、status，端口状态
create_datetime
update_datetime


### 4、ip_attr（属性表）
1、id
2、r_id，对应的ID
3、source，来源（主动或被动接口，如scan/fofa/shodan）
4、tag，标签（通过标签来标识和分类属性，比如操作系统（OPERATION)、中间件（MIDDLEWARE）、应用系统（CMS）等
5、content，属性值
6、hash，md5(r_id+source+tag+content)用于快速查找该属性值是否存在
create_datetime
update_datetime


### 5、port_attr（属性表）
1、id
2、r_id，对应的ID
3、source，来源（主动或被动接口，如scan/fofa/shodan）
4、tag，标签（通过标签来标识和分类属性，比如操作系统（OPERATION)、中间件（MIDDLEWARE）、应用系统（CMS）等
5、content，属性值
6、hash，md5(r_id+source+tag+content)用于快速查找该属性值是否存在
create_datetime
update_datetime


### 6、domain（域名表）
1、id
2、org_id,域名所属组织
3、domain_name，域名
4、status，domain状态
create_datetime
update_datetime


### 7、domain_ip（域名与IP对应关系）
1、id
2、domain_id，域名的ID
3、ip_id，IP的ID
4、status，状态
5、hash,md5(domain_id+ip_id+status)
create_datetime
update_datetime


### 8、domain_attr（属性表）
1、id
2、r_id，对应的ID
3、source，来源（主动或被动接口，如scan/fofa/shodan）
4、tag，标签（通过标签来标识和分类属性，比如操作系统（OPERATION)、中间件（MIDDLEWARE）、应用系统（CMS）等
5、content，属性值
6、hash，md5(r_id+tag+content)用于快速查找该属性值是否存在
create_datetime
update_datetime


### task （任务表）
id
task_id,celery任务id
task_name,任务名称
task_type:任务类型：周期，一次性，
status，任务的状态:started（启动）,success（成功完成）,exception （异常）
params:任务参数，json格式化

create_datetime，任务创建时间
update_datetime，更新时间
finish_datetime，任务结束时间

