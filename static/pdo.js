/**
 * Created by rongfeng on 3/23/2016.
 */

$(document).ready(function () {
    var $input = $("#company_name");
    $(".btn-info").hide();

    var options = {
        url: function (phrase) {
            if (phrase != "") {
                return "http://dev.markitondemand.com/Api/v2/Lookup/jsonp?input=" + phrase;
            }
        },
        getValue: function (msg) {
            return msg.Name + ', ' + msg.Symbol + ', (' + msg.Exchange + ')'
        },
        ajaxSettings: {
            dataType: "jsonp"
        },
        requestDelay: 800
    };
    $input.easyAutocomplete(options);


    var reexp = new RegExp('.*[(].*[)]');       //add company name to com_name_array and prevent duplicate
    var com_name_array = [];
    var com_code_array = [];
    $(".add-company").click(function () {
        if (reexp.test($input.val())) {
            if (com_name_array.length == 0) {
                $(".btn-info").fadeIn('fast');
                com_name_array.push($input.val().split(',')[0]);
                com_code_array.push($input.val().split(',')[1]);
                $(".content-col-right").append('<button type="button" class="btn btn-default com-selected">' + com_name_array[com_name_array.length-1] + '<a class="close">&times;</a></button>');
                $input.val('');
            } else {
                var value2check = $input.val().split(',')[0];
                $.each(com_name_array, function (index, item) {             //maybe consider using callback
                    if (item == value2check) {
                        return false
                    } else if (index + 1 == com_name_array.length) {
                        com_name_array.push($input.val().split(',')[0]);
                        com_code_array.push($input.val().split(',')[1]);
                        $(".content-col-right").append('<button type="button" class="btn btn-default com-selected">' + com_name_array[com_name_array.length-1] + '<a class="close">&times;</a></button>');
                        $input.val('');
                    }
                });
            }
        }
        else {
            alert('No company selected')
        }
    });


    $(document).on('click', '.close', function () {         //remove company icon and remove from com_name_array
        var string_to_check = $(this).parent().text().slice(0, -1);
        $.each(com_name_array, function (index, item) {
            if (item == string_to_check) {
                com_name_array.splice(index,1);
                com_code_array.splice(index,1);
                return false
            }
        });
        $(this).parent().remove();
    });

    var json_response;
    $(".btn-info").click(function () {          // check content before submittion
        $(this).off("click");
        $(this).addClass('disabled');
        $(".add-company").off("click");
        $(".add-company").addClass('disabled');
        post_json();
        $(".jumbotron").fadeToggle();
    });

    var post_json = function () {
        var d2t = {};
        $.each(com_code_array, function (index, item) {     // transform to json schema
            d2t[index.toString()] = item.slice(1, item.length);
        });
        if (com_name_array.length!=0){
            $.ajax({
                url: "/json_r/",
                type: 'POST',
                dataType: 'json',
                data: d2t,
                success: function (response) {
                    json_response = response
                }
            });
        }else{
            alert("Didn't choose any company")
        }
    };


    function getCookie(name) {          // copied from django docs
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    var json_response_parsed = [],
        legend = [];
    $(".list-group-item").click(function () {
        var section = $(this).text();
        if (json_response_parsed.length == 0) {
            $.each(com_code_array, function (index, item) {
                json_response_parsed.push({key: item, value: $.parseJSON(json_response[item.slice(1, item.length)])});
                legend.push({label: item})
            });
            plot_com(json_response_parsed, section, legend);
        } else {
        plot_com(json_response_parsed, section, legend);
        }
    });

    var plot_com = function (array, section2plot, legd) {
        if (array.length > 0) {
            var array2plot = [],
                array_year = [],
                array_number = [],
                figure_array = [];
            $.each(array, function (index, item) {
                array2plot.push(item.value[section2plot])
            });

            $.each(array2plot[0], function (index, item) {
                array_year.push(parseInt(index.slice(0, 4)));
                // array_number.push(parseInt(item));
            });

            $.each(array2plot, function (index, item) {
                $.each(item, function (index2, item2) {
                    if (item2 === null) {
                        array_number.push(null)
                    } else {
                        array_number.push(parseFloat(item2.replace(/,/g, '')));
                    }
                });
                figure_array.push(array_number.slice(0, -1));
                array_number = [];
            });

            var arr_max=0, arr_min=figure_array[0][0];
            $.each(figure_array, function (index, item) {
                $.each(item, function (index2, item2) {
                    if (arr_max < item2){
                        arr_max = item2
                    }
                    if (arr_min > item2){
                        arr_min = item2
                    }
                })
            });
            var temp_var;
            if (arr_max > 0 && arr_max < 100) {
                if (arr_max > 10) {
                    arr_max = (Math.floor(arr_max / 10) + 2) * 10;
                } else {
                    arr_max = Math.floor(arr_max) + 2;
                }
            } else if (arr_max >= 100 && arr_max < 1000) {
                arr_max = (Math.ceil(arr_max / 100) + 0.5) * 100
            } else {
                temp_var = 1;
                while (arr_max > 100) {
                    arr_max /= 10;
                    temp_var *= 10;
                }
                arr_max = (Math.ceil(arr_max) + 5) * temp_var;
            }

            if (arr_min <= 0) {
                if (arr_min > -10) {
                    arr_min = Math.floor(arr_min) - 2
                } else {
                    temp_var = 1;
                    while (arr_min < -100) {
                        arr_min /= 10;
                        temp_var *= 10;
                    }
                    arr_min = (arr_min - 5) * temp_var;
                }
            } else if (arr_min > 0 && arr_min < 100) {
                if (arr_min > 10) {
                    arr_min = (Math.floor(arr_min / 10) - 2) * 10;
                } else {
                    arr_min = Math.floor(arr_min) - 2;
                }
            } else if (arr_min >= 100 && arr_min < 1000) {
                arr_min = (Math.floor(arr_min / 100) - 0.5) * 100
            } else {
                temp_var = 1;
                while (arr_min > 100) {
                    arr_min /= 10;
                    temp_var *= 10;
                }
                arr_min = (Math.floor(arr_min) - 5) * temp_var;
            }

            $.jqplot.config.enablePlugins = true;
            $.jqplot('chartdiv', figure_array,
                {
                    title: section2plot,
                    axes: {
                        yaxis: {min: arr_min, max: arr_max},
                        xaxis: {
                            renderer: $.jqplot.CategoryAxisRenderer,
                            ticks: array_year.slice(0, -1)
                        }
                    },
                    series: legd,
                    legend: {show: true},
                    highlighter: {
                        show: true,
                        sizeAdjust: 7.5,
                        tooltipAxes: 'y'
                    }
                }).replot();
        }
    };

});