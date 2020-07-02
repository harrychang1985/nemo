$(function () {
    $('#btnsiderbar').click();
    $('#tasks-table').DataTable(
        {
            "rowID": 'uuid',
            "paging": false,
            "searching": false,
            "processing": true,
            "serverSide": true,
            "autowidth": false,
            "sort": false,
            "dom": '<t><"bottom"ip>',
            "ajax": {
                "url": "/task-list",
                "type": "post",
                "data": function (d) {
                    return $.extend({}, d, {
                        "task_status": $('#task_status').val()
                    });
                }
            },
            columns: [
                { data: 'uuid', title: 'task-id', width: '10%' },
                { data: 'name', title: '名称', width: '10%' },
                {
                    data: 'state', title: '状态', width: '5%',
                    "render": function (data, type, row) {
                        if (data == 'STARTED') {
                            return data + '<button class="btn btn-sm btn-danger" type="button" onclick="stop_task(\'' + row['uuid'] + '\')" >&nbsp;中止&nbsp;</button>';
                        }
                        else return data;
                    }
                },
                {
                    data: 'kwargs', title: '参数', width: '20%',
                    "render": function (data, type, row) {
                        var data = '<div style="width:100%;white-space:normal;word-wrap:break-word;word-break:break-all;">' + data + '</div>';
                        return data;
                    }
                },
                { data: 'result', title: '结果', width: '10%' },
                { data: 'received', title: '接收时间', width: '10%' },
                { data: 'started', title: '启动时间', width: '10%' },
                { data: 'runtime', title: '执行时长', width: '8%' },
                { data: 'worker', title: 'worker' }
            ]
        }
    );//end datatable

    $("#task_status").change(function () {
        $('#tasks-table').DataTable().draw(false);
    });

    $("#refresh").click(function () {
        $('#tasks-table').DataTable().draw(false);
    });

    //全选 
    $('table th input:checkbox').on(
        'click',
        function () {
            var that = this;
            $(this).closest('table').find(
                'tr > td:first-child input:checkbox').each(
                    function () {
                        this.checked = that.checked;
                        $(this).closest('tr').toggleClass('selected');
                    });

        });

});

function stop_task(uuid) {
    $.post("/task-stop",
        {
            "task-id": uuid,
        }, function (data, e) {
            if (e === "success") {
                swal({
                    title: "中止任务成功！",
                    text: "",
                    type: "success",
                    confirmButtonText: "确定",
                    confirmButtonColor: "#41b883",
                    closeOnConfirm: true,
                    timer: 3000
                },
                    function () {
                        $('#tasks-table').DataTable().draw(false);
                    });
            } else {
                swal('Warning', "中止任务失败!", 'error');
            }
        });
}