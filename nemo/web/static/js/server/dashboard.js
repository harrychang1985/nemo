function get_count_data() {
    //异步获取任务统计信息
    $.post("/dashboard", function (data) {
        $("#task_active").html(data['task_active']);
        $("#task_total").html(data['task_total']);
        $("#domain_count").html(data['domain_count']);
        $("#ip_count").html(data['ip_count']);
    });
}
$(function () {
    var table = $('#tasks-table').DataTable(
        {
            "rowID": 'uuid',
            "paging": false,
            "searching": false,
            "processing": true,
            "serverSide": true,
            "autowidth": true,
            "sort": false,
            "dom": '<t>',
            "ajax": {
                "url": "/task-list",
                "type": "post",
                "data": { start: 0,length:5 } //只显示最近5条记录
            },
            columns: [
                { data: 'task_name', title: '名称', width: '10%' },
                { data: 'state', title: '状态', width: '5%' },
                {
                    data: 'kwargs', title: '参数', width: '30%',
                    "render": function (data, type, row) {
                        var data = '<div style="width:100%;white-space:normal;word-wrap:break-word;word-break:break-all;">' + data + '</div>';
                        return data;
                    }
                },
                { data: 'result', title: '结果', width: '10%' },
                { data: 'received', title: '接收时间', width: '10%' },
                { data: 'started', title: '启动时间', width: '10%' },
                { data: 'runtime', title: '执行时长', width: '8%' },
                { data: 'worker', title: 'worker', width: '8%' ,
                 "render": function (data, type, row) {
                        var data = '<div style="width:100%;white-space:normal;word-wrap:break-word;word-break:break-all;">' + data + '</div>';
                        return data;
                    }
                }
            ]
        }
    );//end datatable
    get_count_data();
    //定时刷新页面
    setInterval(function () {
        table.ajax.reload();
        get_count_data();
    }, 60 * 1000);
});
