$('a.page-link').click(function () {
    //获取页码值
    let form = $('#form-desktop')
    let input = $("<input type='hidden' name='page' value=" + $(this).attr("value") + " />")
    form.append(input)
    form.submit()
})

let myDate = new Date()

function fullNum(num) {
    if (num < 10) {
        return '0' + num
    } else return '' + num
}

if ($('#date-range').attr('value') === '2021/01/01 - 2021/01/01') {
    $('#date-range').attr('value', '2021/01/01 - ' + myDate.getFullYear() + '/' + (fullNum(myDate.getMonth() + 1)) + '/' + fullNum(myDate.getDate()))
}
