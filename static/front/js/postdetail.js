$(function () {
     var ue = UE.getEditor("editor",{
         'serverUrl': '/upload/',
         toolbars: [
                ['undo', 'formatmatch','source','selectall','horizontal'],
                ['removeformat','fontsize','simpleupload','link']
         ]
     });

     // 发表评论
     $('#submit-common').click(function (ev) {
         ev.preventDefault();
         var content = ue.getContent(); //获取评论内容
         var post_id = $('#post_id').val(); //获取评论的帖子id
        $.ajax({
            url:'/addcommon/',
            type:'post',
            data:{
                'post_id':post_id,
                "csrf_token":$("#csrf_token").attr("value"),
                'content':content
            },
            success:function (data) {
                if(data.code == 200) {
                     xtalert.alertSuccessToast("评论成功");
                    window.location.href = '/showpostdetail/?post_id='+post_id
                } else {
                    xtalert.alertConfirm({
                        'msg':'评论之前请先登录',
                        'confirmCallback':function () {
                             window.location.href='/signin/'
                        }
                    })
                }
            }
        })
     })
})







