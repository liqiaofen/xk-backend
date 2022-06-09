function Validator(rule) {
    let val = ''
    let regular = {
        email: '^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+$',
        mobile: ''
    }
    this.is_valid = function (new_val) {
        val = new_val

        if (rule.required && this.validate_required())
            return {
                result: false,
                err_msg: '该字段是必填字段'
            };
        var key;

        for (key in rule) {
            if (key === 'required')
                continue;
            var valid = this['validate_' + key]();
            if (!valid.result) return valid
        }
        return {
            result: true,
            err_msg: ''
        };
    }
    this.validate_required = function () {
        var real = $.trim(val)
        return !real && real !== 0;
    }


    this.validate_length = function (result, key) {
        let res = {
            result: result,
            err_msg: ''
        }
        if (res.result) return res

        if (rule['maxlength'] && rule['minlength']) res.err_msg = '请输入(' + rule.minlength + '-' + rule.maxlength + ')个字符'
        else if (key === 'maxlength') res.err_msg = '输入字符的长度不能大于' + rule.maxlength
        else if (key === 'minlength') res.err_msg = '输入字符的长度不能小于' + rule.minlength
        return res
    }

    this.validate_maxlength = function () {
        val = val.toString()
        return this.validate_length(val.length <= rule.maxlength, 'maxlength')
    }
    this.validate_minlength = function () {
        val = val.toString()
        return this.validate_length(val.length >= rule.minlength, 'minlength')
    }
    this.validate_numberic = function () {
        let res = {
            result: $.isNumeric(val),
            err_msg: ''
        }
        if (!res.result) res.err_msg = '请输入实数'
        return res;
    }


    this.validate_num_size = function (result, key) {
        let res = {
            result: result,
            err_msg: ''
        }
        if (res.result) return res

        if (rule['max'] && rule['min']) res.err_msg = '请输入(' + rule.min + '-' + rule.max + ')之间的数值'
        else if (key === 'max') res.err_msg = '输入小于' + rule.max + '的数值'
        else if (key === 'min') res.err_msg = '输入大于' + rule.min + '的数值'
        return res
    }

    this.validate_max = function () {
        val = parseFloat(val)
        return this.validate_num_size(val <= rule.max, 'max')
    }
    this.validate_min = function () {
        val = parseFloat(val)
        return this.validate_num_size(val >= rule.max, 'min')
    }


    this.validate_pattern = function () {
        var reg = new RegExp(rule.pattern)
        let res = {
            result: reg.test(val),
            err_msg: ''
        }
        if (!res.result) res.err_msg = '请输入合法的值'
        return res
    }
    this.validate_regular = function () {
        return this.validate_re(regular[rule.regular])
    }
    this.validate_re = function (regexp) {
        console.log('regexp', regexp, val)
        var reg = new RegExp(regexp)
        let res = {
            result: reg.test(val),
            err_msg: ''
        }
        if (!res.result) res.err_msg = '请输入合法的值'
        return res
    }


}

function Input(selector) {
    var $ele
        , me = this
        , $error_ele
        , rule = {
        required: true
    };

    this.load_validate = function () {
        this.validator = new Validator(rule);
        listen()
    }

    function listen() {
        //监听

        $ele.on('blur', function () {
            var valid = me.validator.is_valid(me.get_val());
            if (valid.result) {
                $ele.addClass('is-valid')
                $ele.removeClass('is-invalid')
            } else {//显示错误
                $ele.removeClass('is-valid')
                $ele.addClass('is-invalid')
                $('#' + $ele.attr('id') + '-err').html(valid.err_msg)
            }
        })
    }

    function get_error_ele() {
        $error_ele = $(get_error_selector());
    }

    function get_error_selector() {
        return '#' + $ele.attr('name') + '-input-error'
    }

    this.get_val = function () {
        return $ele.val();
    }

    function init() {
        find_ele()
        get_error_ele()
        parse_rule();
        me.load_validate();
    }

    function find_ele() {

        if (selector instanceof jQuery) {
            $ele = selector;
        } else {
            $ele = $(selector)
        }
    }

    function parse_rule() {
        var rule_str = $ele.data('rule')
        if (!rule_str) return;
        var rule_arr = rule_str.split('|')
        var i;
        for (i = 0; i < rule_arr.length; i++) {
            var item = rule_arr[i].split(':');
            rule[item[0]] = JSON.parse(item[1])
        }

    }

    init();
}
Input.get_bind_blur_inputs = function (cur_form_inputs) {
    var form_inputs = []
    cur_form_inputs.each(function (index, node) {
        form_inputs.push(new Input(node))
    })
    return form_inputs
}
Input.input_validate = function (cur_form_inputs) {
    const current_inputs = Input.get_bind_blur_inputs(cur_form_inputs)
    let flag = true
    for (var j = 0; j < current_inputs.length; j++) {
        var r = current_inputs[j].validator.is_valid(current_inputs[j].get_val())
        if (!r.result) {
            flag = false
            break
        }
    }
    return flag
}
function ajax_validate(form_name) {
    $('.is-invalid').removeClass('is-invalid');
    $('.invalid-feedback').text();
    const cur_form_inputs = $(`[data-rule][id^=${form_name}-]`)
    cur_form_inputs.trigger('blur')
    return Input.input_validate(cur_form_inputs)
}

function ajax_error(jqXHR, form_name = null) {
    const res_json = jqXHR.responseJSON
    switch (jqXHR.status) {
        case(400):
            if (form_name) {
                $.each(res_json.errors, function (key, value) {
                    console.log(key, value)
                    var $input = $('#' + form_name + '-' + key);
                    $input.addClass("is-invalid");  // 必须要增加这个类才能显示错误信息
                    $('#' + form_name + '-' + key + '-err').text(value[0])
                })
            } else {
                $.SOW.core.toast.show('danger', '', res_json.msg[0], 'top-center', 10000, true);
            }
            break;

        default:
            if (res_json.msg) {
                $.SOW.core.toast.show('danger', '', res_json.msg, 'top-center', 10000, true);
                break;
            }
            alert('未知错误');

    }
}
$(function () {
    'use strict';
    //获取当前页面的所有表单
    var forms = document.getElementsByTagName('form')
    // var form_input = {} // 记录所有的验证input
    for (var i = 0; i < forms.length; i++) {
        (function (index) {
            //获取表单对应的所有输入框
            var current_form = forms[index]
            var form_id = current_form.id.split('-')[0]
            // 给每个输入框绑定blur验证事件
            const cur_form_inputs = $('[data-rule][id^=' + form_id + '-]')
            Input.get_bind_blur_inputs(cur_form_inputs)

            //给每个提交按钮设置点击事件
            // $('#' + form_id).on('submit', function (e) {
            //     e.preventDefault()
            //     // 触发当前form的所有blur事件，显示校验失败的数据
            //     cur_form_inputs.trigger('blur')
            //
            //     const current_inputs = form_input[form_id]
            //     let flag = Input.input_validate(current_inputs)
            //
            //     // console.log(current_form.method, current_form.action, formData.get('username'))
            //     if (flag) {
            //         var formData = new FormData(current_form);
            //         $.ajax({
            //             url: current_form.action,
            //             type: current_form.method,
            //             data: formData,
            //             processData: false,
            //             contentType: false,
            //             success: function (res) {
            //                 console.log('success', res)
            //                 if (res.status) {
            //
            //                     if (res.data.redirect_to) {
            //                         window.location.href = res.data.redirect_to;
            //                     } else if (res.data.toast) {
            //                         let toast = res.data.toast
            //                         $.SOW.core.toast.show(toast.t_type, toast.t_title, toast.t_body, toast.t_pos, toast.t_delay, toast.t_bg_fill);
            //                     }
            //
            //                 } else {
            //                     $.each(res.errors, function (key, value) {
            //
            //                         let $input = $("#" + form_id + '-' + key);
            //                         $input.addClass("is-invalid");  // 必须要增加这个类才能显示错误信息
            //                         $input.removeClass("is-valid");
            //                         $('#' + $input.attr('id') + '-err').html(value[0])
            //                     })
            //                 }
            //             }
            //         })
            //     }
            // })
        })(i)
    }
    // 选中所有input[data-rule]
    // var $inputs = $('[data-rule]');
    // var inputs = [];
    // var x = '11'

    // console.log(inputs)
    // 解析规则

    // $inputs.each(function (index, node) {
    //     inputs.push(new Input(node))
    // })


    // form_input['login'].trigger('blur')
    // 验证
    // var validator = new Validator('1....5', {
    //     pattern:'^[a-z0-9A-Z]+$'
    // })

    // var result = validator.validate_pattern();
    // console.log(result)

    // var test = new Input('#test');
    // var valid = test.validator.is_valid();
    // console.log('valid', valid)


})