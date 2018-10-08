$(function () {
    $("#addboarder").click(function (ev) {
        xtalert.alertOneInput(swal({
                title: "输入！",
                type: "input",
                showCancelButton: true,
                closeOnConfirm: false,
                animation: "slide-from-top",
                inputPlaceholder: "输入想要添加的板块"
            },
            function (inputValue) {     //保存时输入框不能为空
                if (inputValue === false) return false;
                if (inputValue === "") {
                    swal.showInputError("你需要输入一些话！");
                    return false
                }
                $.ajax({
                    url:'/cms/boarder/',
                    type: 'post',
                    data:{
                        'boardername':inputValue,
                        'postnum':1,
                        'csrf_token':$('meta[name=csrf_token]').attr("value"),
                    },
                    success:function (data) {
                        if (data.code==200){
                            xtalert.alertSuccessToast(data.msg);
                            $('#myModal').modal('hide');
                            window.location.reload(); //  重新加载这个页面
                        }else {
                            xtalert.alertErrorToast(data.msg)
                        }
                    }
                })
            }),
    )
    })
    //删除板块
    $('.delete-btn').click(function (ev) {
        var csrf = $('meta[name=csrf_token]').attr("value");
        ev.preventDefault();
        self = $(this);
        id = self.attr('data-id');
        $.ajax({
            url:'/cms/deleteBoarder/',
            type:'post',
            data: {
                'csrf_token':csrf,
                'id':id
            },
            success:function (data) {
                if (data.code == 200){
                    xtalert.alertSuccessToast("删除成功");
                    window.location.reload();
                }else {
                    xtalert.alertErrorToast(data.msg)
                }
            }
        })
    })


    $('#Modal').on('hidden.bs.modal',function (e) {
        e.preventDefault();
        //当模态视图隐藏,from改为0
        $('#saveBanner').attr("from",'0');
        //每次隐藏情况输入框的值
        $("#boardername").val("");

    })



    $('.update-btn').click(function () {
        self = $(this);
        $('#Modal').modal('show');// 让模态框出来
        $('meta[name=csrf_token]').attr("value");
        $("#boardername").val(self.attr('data-boardername'));
        $('#saveBanner').attr("from",'1')
        $('#id').val(self.attr('data-id'))
    })
    //更新
    $('#saveBanner').click(function (ev) {
        var csrf = $('meta[name=csrf_token]').attr("value");
        var boardername = $("#boardername").val();
        var id = $('#id').val();
        ev.preventDefault();
        console.log("111111111111111111111111")
        self = $(this);//this指的是调用者
        var saveoradd = self.attr('from');
        $.ajax({
            url:'/cms/updateBoarder/',
            type:'post',
            data:{
                'csrf_token':csrf,
                'boardername':boardername,
                'id':id
            },
            success:function (data) {
                if (data.code == 200) {
                    xtalert.alertSuccessToast("更新成功");
                    $('#myModal').modal('hide');
                    window.location.reload();
                } else {
                    xtalert.alertErrorToast(data.msg)
                }
            },
            error:function (err) {
                xtalert.alertErrorToast('请检查网络');
            }
        })
    })

})
