$(document).ready(function () {
    $('#date-range').daterangepicker({
        "showDropdowns": true,
        "showISOWeekNumbers": true,
        "ranges": {
            '今天': [moment(), moment()],
            '昨天': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            '近一周': [moment().subtract(6, 'days'), moment()],
            '近一个月': [moment().subtract(29, 'days'), moment()],
            '近三个月': [moment().subtract(3, 'month'), moment()],
            '近一年': [moment().subtract(1, 'year'), moment()],
        },

        "locale": {
            "format": "YYYY/MM/DD",
            "separator": " - ",
            "applyLabel": "确定",
            "cancelLabel": "取消",
            "fromLabel": "从",
            "toLabel": "到",
            "customRangeLabel": "选择范围",
            "weekLabel": "周",
            "daysOfWeek": [
                "日",
                "一",
                "二",
                "三",
                "四",
                "五",
                "六"
            ],
            "monthNames": [
                "1月",
                "2月",
                "3月",
                "4月",
                "5月",
                "6月",
                "7月",
                "8月",
                "9月",
                "10月",
                "11月",
                "12月"
            ],
            "firstDay": 1
        },
        autoUpdateInput: false,
        "alwaysShowCalendars": true,
        "startDate": "2021年01月01日",
        "endDate": moment(),
        "minDate": "2021年01月01日",
        "linkedCalendars": false,
        "maxDate": moment(),
    }, function (start, end, label) {
        console.log("New date range selected: ' + start.format('YYYY-MM-DD') + ' to ' + end.format('YYYY-MM-DD') + ' (predefined range: ' + label + ')");
    });

    $('input[name="time_range"]').on('apply.daterangepicker', function (ev, picker) {
        $(this).val(picker.startDate.format('YYYY/MM/DD') + ' - ' + picker.endDate.format('YYYY/MM/DD'));
    });
    $('input[name="time_range"]').on('cancel.daterangepicker', function (ev, picker) {
        $(this).val('');
    });
});