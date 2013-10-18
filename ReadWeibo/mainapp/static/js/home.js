function set_category(w_id, category) {
    var paras = {'category': category, 'w_id': w_id}
    $.ajax({
        url: '/set_category/',
        type: 'put',
        dataType: 'json',
        data: JSON.stringify(paras),
        success: function (is_success) {
          if (is_success) {
          }else{
              alert('Fail');
          }
        }
    });
  return false;
}

$(document).ready(function () {
   $(".category").click(function (e) {
    if (!e.target) {
        return;
    }
    wid_cate = e.target.id.split("-")
    set_category(wid_cate[0], wid_cate[1]);
   });
        
});

