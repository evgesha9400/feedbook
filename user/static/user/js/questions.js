$(function() {
    log("loaded questions.js");
    var total_forms = $("input[name='form-TOTAL_FORMS']");
    var q_form = $('#q_form');
    total_forms.val('0');

    q_form.submit(function (e) {
        e.preventDefault();
        var count = 0;
        $("input.answer_text").each(function () {
            if($(this).val()) count++;
        })
        total_forms.val(count)
        log(total_forms.val());
        this.submit();
    })
    function log(message) {
        console.log(message);
    }

    $('input[name*=correct]').change(function () {
        if($(this).closest('.input-group').children('input[type=text]').val()) {
            $('input[name*=correct]').prop('checked', false);
            $(this).prop('checked', true);
        } else {
            $(this).prop('checked', false);
        }
    })

    $("input[type=file]").change(function () {
        if (this.files && this.files[0]) {
            let reader = new FileReader();
            reader.onload = function(e) {
                $("#preview").append(
                    `<img class='rounded' src="${e.target.result}" alt="Preview">`
                );
            };
            reader.readAsDataURL(this.files[0]);
        } else {
            $("#preview").empty();
        }
    })
});
