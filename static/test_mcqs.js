/**
 * Created by rongfeng on 7/18/2016.
 */
$(document).ready(function () {
    $('.alert-danger').hide();
    $('.alert-success').hide();
    $('#q_ans').hide();
    var ans = $('#q_ans').text();
    var ans_submit_btn = $('#ans_submit');
    var chosen;

    $('#submit_button').click(function () {
        $('#submit_button').hide();
        chosen = $('input:radio[name=optradio]:checked').val();
        if(chosen==ans){
            $('.alert-success').show().append(ans+'.');
        }else{
            $('.alert-danger').show().append(ans+'.');
        }
        ans_submit_btn.attr('value', chosen);
        ans_submit_btn.click();
    });
    
});


