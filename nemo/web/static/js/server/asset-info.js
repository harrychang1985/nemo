$(function(){
    $('#btnsiderbar').click();
});
function delete_port_attr(id) {
    swal({
        title: "确定要删除?",
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
                url: '/port-attr-delete/' + id,
                success: function (data) {
                    location.reload();
                },
                error: function (xhr, type) {
                }
            });
        });
}
