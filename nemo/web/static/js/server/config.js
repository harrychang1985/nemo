$(function () {
    $('#btnsiderbar').click();
    load_config();
    //保存配置
    $("#buttonSaveNmap").click(function () {
        save_nmap_config();
    });
    $("#buttonSaveWhatweb").click(function () {
        save_whatweb_config();
    });
});

function load_config() {
    $.post("/adv-config-list", function (data) {
        $('#input_nmap_bin').val(data['nmap']['nmap_bin']);
        $('#input_masscan_bin').val(data['nmap']['masscan_bin']);
        $('#input_nmap_port').val(data['nmap']['port']);
        $('#select_nmap_tech').val(data['nmap']['tech']);
        $('#input_nmap_rate').val(data['nmap']['rate']);
        $('#checkbox_nmap_ping').prop("checked",data['nmap']['ping']);
        $('#input_whatweb_bin').val(data['whatweb']['bin']);
    });
}

function save_nmap_config() {
    swal('Warning', "暂不支持保存配置，请手工修改配置文件!", 'error');
    return ;
    // const nmap_bin = $('#input_nmap_bin').val();
    // const masscan_bin = $('#input_masscan_bin').val();
    // const port = $('#input_nmap_port').val();
    // const tech = $('#select_nmap_tech').val();
    // const rate = $('#input_nmap_rate').val();
    // const ping = $('#checkbox_nmap_ping').is(":checked");
    // if (!nmap_bin) {
    //     swal('Warning', 'NMAP可执行文件不能为空！', 'error');
    //     return;
    // }
    // if (!masscan_bin) {
    //     swal('Warning', 'MASSCAN可执行文件不能为空！', 'error');
    //     return;
    // }
    // if (!tech) {
    //     swal('Warning', '请选择NMAP扫描技术！', 'error');
    //     return;
    // }
    // if (!rate) {
    //     swal('Warning', '请填写NMAP扫描速度！', 'error');
    //     return;
    // }
    // $.post("/adv-config-save-nmap",
    //     {
    //         "nmap_bin": nmap_bin,
    //         "masscan_bin": masscan_bin,
    //         "nmap_port": port,
    //         "nmap_rate": rate,
    //         'nmap_tech': tech,
    //         'nmap_ping': ping
    //     }, function (data, e) {
    //         if (e === "success") {
    //             swal({
    //                 title: "保存配置成功！",
    //                 text: "",
    //                 type: "success",
    //                 confirmButtonText: "确定",
    //                 confirmButtonColor: "#41b883",
    //                 closeOnConfirm: true,
    //                 timer: 3000
    //             });
    //         } else {
    //             swal('Warning', "保存配置失败!", 'error');
    //         }
    //     });
}
function save_whatweb_config() {
    swal('Warning', "暂不支持保存配置，请手工修改配置文件!", 'error');
    return ;
    // const bin = $('#input_whatweb_bin').val();
    // if (!bin) {
    //     swal('Warning', 'Whatweb可执行文件不能为空！', 'error');
    //     return;
    // }
    // $.post("/adv-config-save-whatweb",
    //     {
    //         "whatweb_bin": bin,
    //     }, function (data, e) {
    //         if (e === "success") {
    //             swal({
    //                 title: "保存配置成功！",
    //                 text: "",
    //                 type: "success",
    //                 confirmButtonText: "确定",
    //                 confirmButtonColor: "#41b883",
    //                 closeOnConfirm: true,
    //                 timer: 3000
    //             });
    //         } else {
    //             swal('Warning', "保存配置失败!", 'error');
    //         }
    //     });
}