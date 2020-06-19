$(function () {
    $('#btnsiderbar').click();
    //加载nmap配置
    load_nmap_config();
    // //获取任务的状态信息
    // get_task_status();
    setInterval(function () {
       get_task_status();
    }, 60 * 1000);
    //搜索
    $("#search").click(function () {
        $("#ip_table").DataTable().draw(true);
    });
    //新建任务窗口
    $("#create_task").click(function () {
        var checkIP = [];
        $('#ip_table').DataTable().$('input[type=checkbox]:checked').each(function (i) {
            checkIP[i] = $(this).val();
        });
        $('#text_target').val(checkIP.join("\n"));
        $('#newTask').modal('toggle');
    });
    //执行新建任务Button
    $("#start_task").click(function () {
        const target = $('#text_target').val();
        var port = $('#input_port').val();
        var rate = $('#input_rate').val();
        if (!target) {
            swal('Warning', '请至少输入一个Target', 'error');
            return;
        }
        if (!port) port = "--top-ports 1000";
        if (!rate) rate = 5000;
        $.post("/task-start-portscan",
            {
                "target": target,
                "port": port,
                'rate': rate,
                'nmap_tech': $('#select_tech').val(),
                'org_id': $('#select_org_id_task').val(),
                'iplocation': $('#checkbox_iplocation').is(":checked"),
                'webtitle': $('#checkbox_webtitle').is(":checked"),
                'whatweb': $('#checkbox_whatweb').is(":checked"),
                'ping': $('#checkbox_ping').is(":checked"),
                'fofasearch': $('#checkbox_fofasearch').is(":checked"),
                'shodansearch': $('#checkbox_shodansearch').is(":checked")
            }, function (data, e) {
                if (e === "success" && data['status'] == 'success') {
                    swal({
                        title: "新建任务成功！",
                        text: "TaskId:" + data['result']['task-id'],
                        type: "success",
                        confirmButtonText: "确定",
                        confirmButtonColor: "#41b883",
                        closeOnConfirm: true,
                    },
                        function () {
                            $('#newTask').modal('hide');
                        });
                } else {
                    swal('Warning', "添加任务失败!", 'error');
                }
            });

    });
    //列表全选
    $(".checkall").click(function () {
        alert('ss');
        var check = $(this).prop("checked");
        $(".checkchild").prop("checked", check);
    });
    //IP列表
    $('#ip_table').DataTable(
        {
            "paging": true,
            "serverSide": true,
            "autowidth": false,
            "sort": false,
            "pagingType": "full_numbers",//分页样式
            'iDisplayLength': 20,
            "dom": '<t><"bottom"ip>',
            "ajax": {
                "url": "/ip-list",
                "type": "post",
                "data": function (d) {
                    return $.extend({}, d, {
                        "org_id": $('#select_org_id_search').val(),
                        "ip_address": $('#ip_address').val(),
                        "port": $('#port').val()
                    });
                }
            },
            columns: [
                {
                    data: "id",
                    width: "5%",
                    className: "dt-body-center",
                    title: '<input  type="checkbox" class="checkall" />',
                    "render": function (data, type, row) {
                        return '<input type="checkbox" class="checkchild" value="' + row['ip'] + '"/>';
                    }
                },
                { data: "index", title: "序号", width: "5%" },
                {
                    data: "ip",
                    title: "IP地址",
                    width: "12%",
                    render: function (data, type, row, meta) {
                        return '<a href="/ip-info?ip=' + data + '">' + data + '</a>';
                    }
                },
                { data: "port", title: "开放端口", width: "15%" },
                { data: "title", title: "标题", width: "25%" },
                { data: "banner", title: "Banner", width: "25%" },
                {
                    title: "操作",
                    width: "8%",
                    "render": function (data, type, row, meta) {
                        var strDelete = "<a href=javascript:delete_ip(" + row.id + ")><i class='fa fa-pencil'></i><span>删除</span></a>";
                        return strDelete;
                    }
                }
            ],
            infoCallback: function (settings, start, end, max, total, pre) {
                var api = this.api();
                var pageInfo = api.page.info();
                return "共<b>" + pageInfo.pages + "</b>页,当前显示" + start + "到" + end + "条记录" + ",共有<b>" + total + "</b>条记录";
            },
        }
    );//end datatable
    $(".checkall").click(function() {
        var check = $(this).prop("checked");
        $(".checkchild").prop("checked", check);
    });
});
function load_nmap_config() {
    $.post("/adv-config-list", function (data) {
        $('#input_port').val(data['nmap']['port']);
        $('#select_tech').val(data['nmap']['tech']);
        $('#input_rate').val(data['nmap']['rate']);
        $('#checkbox_ping').prop("checked",data['nmap']['ping']);
    });
}
//删除一个IP
function delete_ip(id) {
    swal({
        title: "确定要删除?",
        text: "该操作会删除这个IP的所有信息！",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "确认删除",
        cancelButtonText: "取消",
        closeOnConfirm: true
    },
        function () {
            $.ajax({
                type: 'post',
                url: '/ip-delete/' + id,
                success: function (data) {
                    $("#ip_table").DataTable().draw(false);
                },
                error: function (xhr, type) {
                }
            });
        });
}
function get_task_status(){
    $.post("/dashboard-task-info", function (data) {
        $("#span_show_task").html(data['task_info']);
    });
}