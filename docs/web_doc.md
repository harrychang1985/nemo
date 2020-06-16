## Router ##

---

### 0x01 登录认证 ###

静态用户登录，即后台设置登录用户名和密码，采用vali-admin前端的locked-login页面，只需要输入管理员密码就可以登录后台。（目前是内测工具，为了方便调试）

路径：/login
请求方法：GET POST
请求方式：jquery
参数：password

### 0x02 后台管理 ###

后台管理主要分以下几个模块：

+ 仪表面板： 展示系统的总体资产情况，如资产总数、漏洞数量、弱口令数量等

+ 机构管理： 这个功能模块主要是用于管理资产一个归属属性，也即是资产属于哪个机构的，便于定位。

+ 资产管理： 目前只展示IP资产和域名资产

+ 任务管理： 用于对资产进行操作的，可新建任务，查看任务等，任务分多种类型，比如端口扫描、信息收集、域名收集等。

#### 0x00 仪表面板 ####

#### 0x01 机构管理 ####

+ 添加机构

    路径： /org-add
    请求方法： GET POST
    参数：data = {'org_name': '机构名称', 'stauts': '机构状态', 'sort_order':''}

+ 机构列表

    路径: /org-list
    请求方法： POST
    参数：jquery.dataTable
    采用jquery的数据报插件展示数据，在dataTable中采用ajax向服务器发起请求，服务端进行数据查询后返回json数据。
    返回：json_data = {'draw': draw, 'data': org_list, 'recordsTotal': count, 'recordsFilter': count}

#### 0x02 资产管理 ####

+ 添加资产
    路径： /asset-add

+ IP资产
    路径： /ip-asset-list

+ 域名资产
    路径： /domain-asset-list

#### 0x03 任务管理 ####

+ 新建任务
    路径：/task-add

+ 任务列表
    路径：/task-list
