$(function () {
    $('#btnsiderbar').click();
    $('#select_org_id_search').val($('#hidden_org_id').val());
    $('#select_org_id_task').val($('#hidden_org_id').val());
    //获取任务的状态信息
    //get_task_status();
    setInterval(function () {
        get_task_status();
    }, 60 * 1000);
    //搜索任务
    $("#search").click(function () {
        $("#domain_table").DataTable().draw(true);
    });
    //显示创建任务
    $("#create_task").click(function () {
        var checkIP = [];
        $('#domain_table').DataTable().$('input[type=checkbox]:checked').each(function (i) {
            checkIP[i] = $(this).val();
        });
        $('#text_target').val(checkIP.join("\n"));
        $('#newTask').modal('toggle');
    });
    //启动任务 
    $("#start_task").click(function () {
        const target = $('#text_target').val();
        if (!target) {
            swal('Warning', '请至少输入一个Target', 'error');
            return;
        }
        $.post("/task-start-domainscan",
            {
                "target": target,
                'org_id': $('#select_org_id_task').val(),
                'subdomain': $('#checkbox_subdomain').is(":checked"),
                'webtitle': $('#checkbox_webtitle').is(":checked"),
                'whatweb': $('#checkbox_whatweb').is(":checked"),
                'fld_domain': $('#checkbox_fld_domain').is(":checked"),
                'portscan': $('#checkbox_portscan').is(":checked"),
                'fofasearch': $('#checkbox_fofasearch').is(":checked"),
                'networkscan': $('#checkbox_networkscan').is(":checked"),
                'subtask': $('#checkbox_subtask').is(":checked")
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
    $("#export_excel").click(function () {
        var url = 'domain-export?';
        url += 'org_id=' + encodeURI($('#select_org_id_search').val());
        url += '&ip_address=' + encodeURI($('#ip_address').val());
        url += '&domain_address=' + encodeURI($('#domain_address').val());
        window.open(url);
    });
    $('#domain_table').DataTable(
        {
            "paging": true,
            "serverSide": true,
            "autowidth": false,
            "sort": false,
            "pagingType": "full_numbers",//分页样式
            'iDisplayLength': 50,
            "dom": '<i><t><"bottom"lp>',
            "ajax": {
                "url": "/domain-list",
                "type": "post",
                "data": function (d) {
                    return $.extend({}, d, {
                        "org_id": $('#select_org_id_search').val(),
                        "ip_address": $('#ip_address').val(),
                        "domain_address": $('#domain_address').val()
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
                        return '<input type="checkbox" class="checkchild" value="' + row['domain'] + '"/>';
                    }
                },
                { data: "index", title: "序号", width: "5%" },
                {
                    data: "domain",
                    title: "域名",
                    width: "12%",
                    render: function (data, type, row, meta) {
                        return '<a href="/domain-info?domain=' + data + '" target="_blank">' + data + '</a>';
                    }
                },
                { data: "ip", title: "IP地址", width: "20%" },
                {
                    data: "title", title: "标题", width: "25%",
                    "render": function (data, type, row, meta) {
                        var title=data.substr(0,100);
                        if(data.length>100) title += '......';
                        var strData = '<div style="width:100%;white-space:normal;word-wrap:break-word;word-break:break-all;">' + title + '</div>'
                        return strData;
                    }
                },
                {
                    data: "banner", title: "Banner", width: "25%",
                    "render": function (data, type, row, meta) {
                        var title=data.substr(0,100);
                        if(data.length>100) title += '......';
                        var strData = '<div style="width:100%;white-space:normal;word-wrap:break-word;word-break:break-all;">' + title + '</div>'
                        return strData;
                    }
                },
                {
                    title: "操作",
                    width: "10%",
                    "render": function (data, type, row, meta) {
                        var strDelete = "<a class=\"btn btn-sm btn-danger\" href=javascript:delete_domain(" + row.id + ") role=\"button\" title=\"Delete\"><i class=\"fa fa-trash-o\"></i></a>";
                        return strDelete;
                    }
                }
            ],
            infoCallback: function (settings, start, end, max, total, pre) {
                var api = this.api();
                var pageInfo = api.page.info();
                return "共<b>" + total + "</b>条记录，当前显示" + start + "到" + end + "记录";
            },
        }
    );//end datatable
    $(".checkall").click(function () {
        var check = $(this).prop("checked");
        $(".checkchild").prop("checked", check);
    });
});

function delete_domain(id) {
    swal({
        title: "确定要删除?",
        text: "该操作会删除这个域名的所有信息！",
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
                url: '/domain-delete/' + id,
                success: function (data) {
                    $("#domain_table").DataTable().draw(false);
                },
                error: function (xhr, type) {
                }
            });
        });
}

function get_task_status() {
    $.post("/dashboard-task-info", function (data) {
        $("#span_show_task").html(data['task_info']);
    });
}
