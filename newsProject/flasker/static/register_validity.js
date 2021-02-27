password = document.getElementById("password")
password_confirm = document.getElementById("password_confirm")

submit = document.getElementById("submit")

submit.addEventListener("focusin", function (e) {
        //检测密码一致
        if (!(password.value === password_confirm.value)) {
            e.stopPropagation()
            password_confirm.setCustomValidity('请确保与密码一致');
            submit.click()
        }
        else {
            password_confirm.setCustomValidity('');
            submit.click()
        }
    }
)
