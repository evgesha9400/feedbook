$(function() {
    // ajaxSetup code from https://gist.github.com/alanhamlett/6316427
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (settings.type == 'POST' || settings.type == 'PUT' || settings.type == 'DELETE') {
                function getCookie(name) {
                    let cookieValue = null;
                    if (document.cookie && document.cookie != '') {
                        let cookies = document.cookie.split(';');
                        for (let i = 0; i < cookies.length; i++) {
                            let cookie = jQuery.trim(cookies[i]);
                            // Does this cookie string begin with the name we want?
                            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            }
        }
    });

    var websocket_url = 'wss://' + window.location.host + '/ws/session/' + session_id + '/';
    var socket = new ReconnectingWebSocket(websocket_url);

    var chat = $("#chat");
    var message_input = $('#message_input');
    var send_message_btn = $('#send_message_btn');
    var current_question, current_choices;

    //question overlay and its children
    var question_overlay = $('#question_overlay');
    var question_timer = $('#question_timer');
    var question_image = $('#question_image');
    var question_text = $('#question_text');
    var choice_row1 = $('#choice_row1');
    var choice_row2 = $('#choice_row2');

    message_input.focus();

    message_input.keydown(function(e) {
        if(e.which === 13) {
            send_message_btn.click();
        }
    });

    socket.onopen = function(e) {};

    socket.onclose = function(e) {};

    socket.onmessage = function(e) {

        var data = JSON.parse(e.data);
        var response_type = data['response_type'];
        console.log(response_type)
        switch (response_type) {
            case 'timer':
                change_timer(data);
                break;
            case 'message':
                add_message_to_chat(data);
                break;
            case 'like':
                like_message(data);
                break;
            case 'ask':
                ask_question(data);
                break;
            case 'disconnect':
                window.location.href = '/user/home';
                console.log("disconnect")
        }
    };

    send_message_btn.click(function () {
        var data = {
            'request_type' : "message",
            'text': message_input.val()
        };
        send_to_socket(data);
        message_input.val("");
    });

    chat.on("click", ".message_likes input", function () {
        console.log('like clicked');
        var data = {
            'request_type' : 'like',
            'id': $(this).closest('tr').attr('id').replace('m_', '')
        };
        send_to_socket(data);
    });

    question_overlay.on("click", ".rq_answer", function () {
        console.log("rq_answer_clicked")
        var answer = $("#rq_text").val();
        console.log(answer);
        var q_id = current_question.pk;
        clean_choices();
        answer_question(q_id, answer);
    })

    question_overlay.on("click", ".mcq_answer", function () {
        console.log("mcq_answer_clicked")
        var answer = $(this).text();
        var q_id = current_question.pk;
        clean_choices();
        answer_question(q_id, answer);
    })

    function send_to_socket(data) {
        socket.send(JSON.stringify(data));
    }

    function add_message_to_chat(data) {
        var new_message_DOM = `        <tr id=m_${data['id']} class="message">
          <td class="message_text text-center">${data['text']}</td>
          <td class="message_likes text-right">
          <input type="image" src="/static/session/images/like.png" alt="like"/>
          <span class="count">${data['likes']}</span>
          </td>
        </tr>`
        chat.append(new_message_DOM);
    }

    function like_message(data) {
        $('#m_' + data['id'] + " .message_likes .count").text(data['likes']);
        sort_messages();
    }

    // modified code from https://www.w3schools.com/howto/howto_js_sort_table.asp
    function sort_messages() {
        console.log("sorting...")
      var table, rows, switching, i, x, y, shouldSwitch;
      table = document.getElementById("chat");
      switching = true;

      while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 0; i < (rows.length - 1); i++) {
          shouldSwitch = false;
          x = rows[i].getElementsByClassName("message_likes")[0];
          x = x.getElementsByTagName('span')[0]
          y = rows[i + 1].getElementsByClassName("message_likes")[0];
          y = y.getElementsByTagName('span')[0]
          if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
            shouldSwitch = true;
            break;
          }
        }
        if (shouldSwitch) {
          rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
          switching = true;
        }
      }
    }

    function ask_question(data) {
        let question = JSON.parse(data['question'])[0];
        let choices = JSON.parse(data['choices']);
        let choices_num = choices.length;
        set_current(question, choices);
        clean_questions();
        switch (choices_num) {
            case 0:
            case 1:
                display_regular_question(question);
                break;
            case 2:
            case 3:
            case 4:
                display_multiple_choice(question, choices);
                break;
        }
    }


    function answer_question(q_id, text) {
        $.post(session_id+'/answer', {q_id:q_id, text:text}, function (data) {
            if(data['response']) {
                console.log("answer " + data['response']);
            } else {
                console.log("!answer " + data['response']);
            }
        })
    }

    function set_current(question, choices) {
        current_question = question;
        current_choices = choices;
    }

    function display_regular_question(question){
        let timeout = question.fields.timeout;
        fill_question(question);
        choice_row1.append(get_rq_input());
        question_overlay.show();
    }

    function display_multiple_choice(question, choices){
        let timeout = question.fields.timeout;
        fill_question(question);
        fill_choices(choices);
        question_overlay.show();
    }

    function fill_question(question) {
        let fields = question.fields;
        question_timer.text(fields.timeout);
        question_text.text(fields.text);
        if(fields.image !== "") {
            let url = media_url+fields.image;
            let img_DOM = `<img src="${url}" alt="missing image">`;
            question_image.append(img_DOM);
        }

    }

    function fill_choices(choices) {
        for(var index in choices){
            let id = choices[index].pk;
            let text = choices[index].fields.text;
            let btn = get_mcq_input(index, text);
            if (index < 2){
                choice_row1.append(btn);
            } else if (index < 4){
                choice_row2.append(btn);
            }
        }
    }

    function clean_current() {
        current_question = "";
        current_choices = "";
    }

    function clean_questions() {
        question_text.empty();
        question_timer.empty();
        question_image.empty();
        clean_choices();
    }

    function clean_choices() {
        choice_row1.empty();
        choice_row2.empty();
    }

    function get_mcq_input(index, text) {
        switch (index) {
            case "0":
                return `<p class="mcq_answer btn btn-primary text-center m-1"> ${text} </p>`;
            case "1":
                return `<p class="mcq_answer btn btn-danger text-center m-1"> ${text} </p>`;
            case "2":
                return `<p class="mcq_answer btn btn-info text-center m-1"> ${text} </p>`;
            case "3":
                return `<p class="mcq_answer btn btn-success text-center m-1"> ${text} </p>`;
            default:
                break;

        }
    }

    function get_rq_input() {
        return `                         <div class="input-group">

                                            <input type="text" id='rq_text' class="form-control" placeholder="Please enter your response">

                                            <div class="input-group-append">
                                                <input type="button" class="rq_answer btn btn-outline-dark" value="Submit">
                                            </div>

                                        </div>`;
    }

    function change_timer(data) {
        let seconds = data["seconds"];
        question_timer.text(seconds);
        if(seconds<1) {
            question_overlay.hide();
            clean_questions();
            clean_current();
        }
    }

});