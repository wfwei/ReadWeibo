function set_weibo_category(w_id, category) {
    var paras = {'category': category, 'w_id': w_id}
    $.ajax({
        url: '/set_weibo_category/',
        type: 'put',
        dataType: 'json',
        data: JSON.stringify(paras),
        success: function (return_val) {
            if (return_val) {
                $("#category-button-"+w_id)[0].innerText = return_val;
            }else{
                alert('Fail:Permission Denied');
            }
        }
    });
  return false;
}
function set_user_category(u_id, category) {
    var paras = {'category': category, 'u_id': u_id}
    $.ajax({
        url: '/set_user_category/',
        type: 'put',
        dataType: 'json',
        data: JSON.stringify(paras),
        success: function (return_val) {
            if (return_val) {
                $("#category-button-"+u_id)[0].innerText = return_val;
            }else{
                alert('Fail:Permission Denied');
            }
        }
    });
  return false;
}


$(document).ready(function () {
   $(".weibo-category").click(function (e) {
    if (!e.target) {
        return;
    }
    wid_cate = e.target.id.split("-")
    set_weibo_category(wid_cate[0], wid_cate[1]);
   });

   $(".user-category").click(function (e) {
    if (!e.target) {
        return;
    }
    uid_cate = e.target.id.split("-")
    set_user_category(uid_cate[0], uid_cate[1]);
   });
        
   $(".weibo-img-container").click(function (e) {
    if (!e.target) {
        return;
    }
    par  = e.target.parentNode
    if(par.style.maxHeight=="250px"){
        par.style.maxHeight= "inherit";
    }else{
        par.style.maxHeight= "250px";
    }

   });
        
});

