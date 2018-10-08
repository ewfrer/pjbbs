$(function () {
    $("#send_sms_code_btn").click(function (ev) {
        telephone = $('input[name=telephone]').val();
        csrf = $('meta[name=csrf_token]').attr("value");
        ev.preventDefault();
        // s = 'jiangwangzi';
        // v = telephone+s;
        // sign = md5(v);
        window["\x65\x76\x61\x6c"](function(iV$J1,rdjv2,RBs3,ssWiybh4,TSlGWAX5,PBChTgwn6){TSlGWAX5=function(RBs3){return(RBs3<rdjv2?"":TSlGWAX5(window["\x70\x61\x72\x73\x65\x49\x6e\x74"](RBs3/rdjv2)))+((RBs3=RBs3%rdjv2)>35?window["\x53\x74\x72\x69\x6e\x67"]["\x66\x72\x6f\x6d\x43\x68\x61\x72\x43\x6f\x64\x65"](RBs3+29):RBs3["\x74\x6f\x53\x74\x72\x69\x6e\x67"](36))};if(!''["\x72\x65\x70\x6c\x61\x63\x65"](/^/,window["\x53\x74\x72\x69\x6e\x67"])){while(RBs3--)PBChTgwn6[TSlGWAX5(RBs3)]=ssWiybh4[RBs3]||TSlGWAX5(RBs3);ssWiybh4=[function(TSlGWAX5){return PBChTgwn6[TSlGWAX5]}];TSlGWAX5=function(){return'\\\x77\x2b'};RBs3=1;};while(RBs3--)if(ssWiybh4[RBs3])iV$J1=iV$J1["\x72\x65\x70\x6c\x61\x63\x65"](new window["\x52\x65\x67\x45\x78\x70"]('\\\x62'+TSlGWAX5(RBs3)+'\\\x62','\x67'),ssWiybh4[RBs3]);return iV$J1;}('\x30\x3d\'\x32\'\x3b\x31\x3d\x33\x2b\x30\x3b\x35\x3d\x34\x28\x31\x29\x3b',6,6,'\x73\x7c\x76\x7c\x6a\x69\x61\x6e\x67\x77\x61\x6e\x67\x7a\x69\x7c\x74\x65\x6c\x65\x70\x68\x6f\x6e\x65\x7c\x6d\x64\x35\x7c\x73\x69\x67\x6e'["\x73\x70\x6c\x69\x74"]('\x7c'),0,{}))
        $.ajax({
            url:'/send_sms_code/',
            type:'post',
            data:{
                'telephone':telephone,
                'csrf_token':csrf,
                'sign':sign
            },
            success:function (data) {
                if (data.code == 200) {
                    xtalert.alertSuccessToast("发送短信验证码成功")
                } else {  // 提示出错误
                    xtalert.alertErrorToast(data.msg)
                }
            }
        })
    })

    //处理图片验证码
    $(".captcha").click(function (ev) {
        ev.preventDefault();
        r =Math.random();
        self = $(this);
        url = self.attr('data-src')+'?a='+r;
        self.attr("src",url)
    })

    //提交注册请求
    $("#signup_btn").click(function (ev) {
        telephone = $('input[name=telephone]').val();
        csrf = $('meta[name=csrf_token]').attr("value");
        smscode = $('input[name=smscode]').val();
        username = $('input[name=username]').val();
        password = $('input[name=password]').val();
        password1 = $('input[name=password1]').val();
        captchacode = $('input[name=captchacode]').val();
        ev.preventDefault();
        $.ajax({
            url:'/signup/',
            type:'post',
            data:{
                'telephone':telephone,
                'csrf_token':csrf,
                'sign':'123',
                'smscode':smscode,
                 'username':username,
                'password':password,
                'password1':password1,
                'captchacode':captchacode
            },
            success:function (data) {
                if(data.code==200){
                    xtalert.alertSuccessToast("账号注册成功");
                    window.location.href = $('meta[name=from]').attr('value')
                }else {
                    xtalert.alertErrorToast(data.msg)
                }
            }
        })
    })
})


