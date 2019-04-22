$(function() {

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
    var current_question, current_choices;

    //teacher
    var host_panel = $(".host_panel");
    var close_session = $("#close_session");
    var connected_users = $('#connected_users');

    //question overlay and its children
    var question_overlay = $('#question_overlay');
    var question_timer = $('#question_timer');
    var question_image = $('#question_image');
    var question_text = $('#question_text');
    var choice_row1 = $('#choice_row1');
    var choice_row2 = $('#choice_row2');


    host_panel.on("click", ".ask", function() {
        var data = {
            'request_type': 'ask',
            'id': $(this).closest('tr').attr('id').replace('q_', '')
        };
        send_to_socket(data);
        $(this).closest('tr').remove();
    });

    question_overlay.on("click", "#close_poll", function () {
        question_overlay.hide();
        clean_questions();
    });

    close_session.click(function () {
        var data = {
            'request_type': 'close'
        }
        send_to_socket(data);
    })

    socket.onopen = function(e) {};

    socket.onclose = function(e) {};

    socket.onmessage = function(e) {

        var data = JSON.parse(e.data);
        var response_type = data['response_type'];
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
            case 'answer_poll':
                show_answer_poll(data);
                break;
            case 'users_change':
                users_change(data);
                break;
            case 'disconnect':
                window.location.href = '/user/home';
        }
    };

    function send_to_socket(data) {
        socket.send(JSON.stringify(data));
    }

    function users_change(data) {
        var user_count = data['user_count'];
        var str = connected_users.text().replace(/\d+/, user_count);
        connected_users.text(str);
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

    function set_current(question, choices) {
        current_question = question;
        current_choices = choices;
    }

    function display_regular_question(question){
        let timeout = question.fields.timeout;
        fill_question(question);
        start_timer(timeout);
    }

    function display_multiple_choice(question, choices){
        let timeout = question.fields.timeout;
        fill_question(question);
        fill_choices(choices);
        start_timer(timeout);
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

    function start_timer(seconds) {
        question_overlay.show();
        let interval = setInterval(function () {
            seconds--;
            send_to_socket({
                "request_type": "timer",
                "seconds": seconds
            })
            if(seconds<1) {
                clearInterval(interval);
            }
        }, 1000);
    }

    function change_timer(data) {
        let seconds = data["seconds"];
        question_timer.text(seconds);
        if(seconds<1) {
            question_overlay.hide();
            clean_questions();
            send_to_socket({'request_type': 'answer_poll', 'q_id': current_question.pk});
            clean_current();
        }
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

    function show_answer_poll(data) {
        let answers = data['answers']
        console.log(answers);
        let labels = [], values = []
        for(let answer in answers){
            labels.push(answers[answer][0]);
            values.push(answers[answer][1]);
        }
        let canvas = `<div id="answer_poll" style="height: 70vh;">
                        <canvas id="chart" class="bg-white" width="300" height="200"></canvas>
                      </div>`
        Chart.defaults.global.responsive = true;
        Chart.defaults.global.maintainAspectRatio = false;
        let fillColor = 'rgba(54, 162, 235, 0.5)';
        let outlineColor = 'rgba(54, 162, 235, 0.5)';
        let len = labels.length;
        let backgroundColor = new Array(len).fill(fillColor, 0, len);
        let borderColor = new Array(len).fill(outlineColor, 0, len);

        question_text.append(canvas)
        choice_row2.append('<input type="button" id="close_poll" value="Close" class="btn btn-outline-dark">')
        question_overlay.show();
        let chart = new Chart($("#chart"), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Responses',
                    data: values,
                    backgroundColor: backgroundColor,
                    borderColor: borderColor,
                    borderWidth: 1
                }
                ]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true,
                            stepSize: 1
                        }
                    }]
                }
            }
        });
    }
});