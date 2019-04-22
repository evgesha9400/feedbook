from .forms import RegistrationForm, SubjectForm, QuestionChoiceFormset, LessonForm, QuestionForm
from session.forms import SessionConnectForm, SessionCreateForm
from .models import Subject, Question, Lesson, QuestionChoice

from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count


def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password2')
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'user/register.html', {'form': form})
    else:
        return render(request, 'user/register.html', {'form': form})


@login_required
def home(request):
    if request.method == "GET":
        connect_form = SessionConnectForm()
        create_form = SessionCreateForm(user=request.user)
        context = {
            'connect_form': connect_form,
            'create_form': create_form
        }
        return render(request, 'user/home.html', context)


@login_required
def connect_to_session(request):
    if request.method == "GET":
        form = SessionConnectForm(request.GET.copy())
        if form.is_valid():
            return redirect('session', form.data.get('session_id'))
        else:
            form.data['session_id'] = None
            create_form = SessionCreateForm(user=request.user)
            context = {
                'connect_form': form,
                'create_form': create_form
            }
            return render(request, 'user/home.html', context)


@login_required
def subjects(request):
    if request.method == "GET":
        return render(request, 'user/subjects.html')
    else:
        return HttpResponseBadRequest


@login_required
def add_subject(request):
    if request.method == "GET":
        context = dict(s_form=SubjectForm(user=request.user))
        return render(request, 'user/subject_create.html', context)
    elif request.method == "POST":
        s_form = SubjectForm(request.POST, user=request.user)
        if s_form.is_valid():
            s = s_form.save(commit=False)
            s.user = request.user
            s.save()
            return redirect('lessons', s.id)
        else:
            context = dict(s_form=s_form)
            return render(request, 'user/subject_create.html', context)
    else:
        return HttpResponseBadRequest


@login_required
def update_subject(request, s_id):
    try:
        subject = request.user.subjects.get(pk=s_id)
    except Subject.DoesNotExist:
        messages.warning(request, f'Subject Does Not exist')
        return redirect('subjects')
    if request.method == "POST":
        s_form = SubjectForm(request.POST, instance=subject, user=request.user)
        if s_form.is_valid():
            s_form.save()
            return redirect('subjects')
        else:
            return render(request, 'user/subject_update.html', dict(s_form=s_form, user=request.user))
    elif request.method == "GET":
        context = dict(s_form=SubjectForm(instance=subject, user=request.user))
        return render(request, 'user/subject_update.html', context)
    else:
        return HttpResponseBadRequest


@login_required
def delete_subject(request, s_id):
    try:
        subject = request.user.subjects.get(pk=s_id)
    except Subject.DoesNotExist:
        messages.warning(request, f'Subject Does Not exist')
        return redirect('subjects')
    if request.method == "POST":
        subject.delete()
        return redirect('subjects')
    else:
        return HttpResponseBadRequest


@login_required
def lessons(request, s_id):
    if request.method == "GET":
        context = dict(subject=request.user.subjects.get(pk=s_id))
        return render(request, 'user/lessons.html', context)
    else:
        return HttpResponseBadRequest


@login_required
def add_lesson(request, s_id):
    try:
        subject = request.user.subjects.get(pk=s_id)
    except Subject.DoesNotExist:
        return redirect('subjects')

    if request.method == "POST":
        l_form = LessonForm(request.POST)
        if l_form.is_valid():
            new_lesson = l_form.save(commit=False)
            new_lesson.subject = request.user.subjects.get(pk=s_id)
            new_lesson.save()
            return redirect('questions', s_id, new_lesson.id)
        else:
            context = {
                'subject': subject,
                'l_form': l_form,
            }
            return render(request, 'user/lesson_create.html', context)
    elif request.method == "GET":
        context = {
            'subject': subject,
            'l_form': LessonForm(initial={'number': subject.lessons.count()+1}),
        }
        return render(request, 'user/lesson_create.html', context)


@login_required
def update_lesson(request, s_id, l_id):

    try:
        subject = request.user.subjects.get(pk=s_id)
        lesson = subject.lessons.get(pk=l_id)
    except Subject.DoesNotExist:
        return redirect('subjects')
    except Lesson.DoesNotExist:
        return redirect('lessons', s_id)

    if request.method == "POST":
        l_form = LessonForm(request.POST, instance=lesson)
        if l_form.is_valid():
            l_form.save()
            return redirect('lessons', s_id)
        else:
            context = dict(l_form=l_form)
            messages.warning(request, f"Invalid form")
            return render(request, 'user/lesson_update.html', context)
    elif request.method == "GET":
        l_form = LessonForm(instance=lesson)
        context = dict(subject=subject, l_form=l_form)
        return render(request, 'user/lesson_update.html', context)
    else:
        return HttpResponseBadRequest


@login_required
def delete_lesson(request, s_id, l_id):
    if request.method == "POST":
        try:
            subject = request.user.subjects.get(pk=s_id)
            subject.lessons.get(pk=l_id).delete()
        except Subject.DoesNotExist:
            pass
        except Lesson.DoesNotExist:
            pass
        return redirect('lessons', s_id)


@login_required
def questions(request, s_id, l_id):
    if request.method == "GET":
        try:
            subject = request.user.subjects.get(pk=s_id)
            lesson = subject.lessons.get(pk=l_id)
        except Subject.DoesNotExist:
            messages.warning(request, f'Subject does not exist')
            return redirect('subjects')
        except Lesson.DoesNotExist:
            messages.warning(request, f'Lesson does not exist')
            return redirect('lessons', s_id)
        context = dict(subject=subject, lesson=lesson)
        return render(request, 'user/questions.html', context)
    else:
        return HttpResponseBadRequest


@login_required
def add_question(request, s_id, l_id):
    try:
        subject = request.user.subjects.get(pk=s_id)
        lesson = subject.lessons.get(pk=l_id)
    except Subject.DoesNotExist:
        messages.warning(request, f'Subject does not exist')
        return redirect('subjects')
    except Lesson.DoesNotExist:
        messages.warning(request, f'Lesson does not exist')
        return redirect('lessons', s_id)

    if request.method == "POST":
        q_form = QuestionForm(request.POST, request.FILES)
        qc_formset = QuestionChoiceFormset(request.POST)
        if q_form.is_valid() and qc_formset.is_valid():
            new_question = q_form.save(commit=False)
            new_question.lesson = lesson
            new_question.save()
            for form in qc_formset:
                new_choice = form.save(commit=False)
                new_choice.question = new_question
                new_choice.save()

            messages.success(request, f'Question added')
            return redirect('questions', s_id, l_id)
        else:
            context = {
                'subject': subject,
                'lesson': lesson,
                'q_form': q_form,
                'qc_formset': qc_formset
            }
            return render(request, 'user/question_create.html', context)
    else:
        context = {
            'subject': subject,
            'lesson': lesson,
            'q_form': QuestionForm(),
            'qc_formset': QuestionChoiceFormset(queryset=QuestionChoice.objects.none())
        }
        return render(request, 'user/question_create.html', context)


@login_required
def update_question(request, s_id, l_id, q_id):
    try:
        subject = request.user.subjects.get(pk=s_id)
        lesson = subject.lessons.get(pk=l_id)
        question = lesson.questions.get(pk=q_id)
    except Subject.DoesNotExist:
        messages.warning(request, f'Subject does not exist')
        return redirect('subjects')
    except Lesson.DoesNotExist:
        messages.warning(request, f'Lesson does not exist')
        return redirect('lessons', s_id)
    except Question.DoesNotExist:
        messages.warning(request, f'Question does not exist')
        return redirect('questions', s_id, l_id)

    if request.method == "POST":
        q_form = QuestionForm(request.POST or None, request.FILES or None, instance=question)
        qc_formset = QuestionChoiceFormset(request.POST, queryset=question.choices.all())
        to_exclude = []
        for form in qc_formset:
            to_exclude.append(form.instance.pk)
        if q_form.is_valid() and qc_formset.is_valid():
            q = q_form.save()
            qcs = qc_formset.save(commit=False)
            for qc in qcs:
                to_exclude.append(qc.pk)
                qc.question = q
                qc.save()
            q.choices.all().exclude(pk__in=to_exclude).delete()
            return redirect('questions', s_id, l_id)
        else:
            messages.warning(request, f'Invalid form data')
            context = {
                'subject': subject,
                'lesson': lesson,
                'q_form': QuestionForm(instance=question),
                'qc_formset': QuestionChoiceFormset(queryset=question.choices.all())
            }
            return render(request, 'user/question_update.html', context)
    else:
        context = {
            'subject': subject,
            'lesson': lesson,
            'q_form': QuestionForm(instance=question),
            'qc_formset': QuestionChoiceFormset(queryset=question.choices.all())
        }
        return render(request, 'user/question_update.html', context)


@login_required
def delete_question(request, s_id, l_id, q_id):
    try:
        subject = request.user.subjects.get(pk=s_id)
        lesson = subject.lessons.get(pk=l_id)
        question = lesson.questions.get(pk=q_id)
    except Subject.DoesNotExist:
        messages.warning(request, f'Subject does not exist')
        return redirect('subjects')
    except Lesson.DoesNotExist:
        messages.warning(request, f'Lesson does not exist')
        return redirect('lessons', s_id)
    except Question.DoesNotExist:
        messages.warning(request, f'Question does not exist')
        return redirect('questions', s_id, l_id)

    if request.method == "POST":
        question.delete()
        return redirect('questions', s_id, l_id)
    else:
        return HttpResponseBadRequest


@login_required
def statistics(request):
    if request.method == "GET":
        sessions = request.user.taught_session.values("subject_code", "subject_name").distinct()
        return render(request, 'user/statistics.html', dict(sessions=sessions))
    else:
        return HttpResponseBadRequest


@login_required
def subject_statistics(request, subject_code):
    if request.method == "GET":
        sessions = request.user.taught_session.filter(subject_code=subject_code)
        return render(request, 'user/statistics_subject.html', dict(sessions=sessions))
    else:
        return HttpResponseBadRequest


@login_required
def subject_graphs(request, subject_code):
    if request.method == "GET":
        label1 = []
        correct = []
        wrong = []
        none = []
        sessions = request.user.taught_session.filter(subject_code=subject_code).order_by('start_time')
        connected = list(sessions.values_list("user_count", flat=True))
        label2 = list(sessions.values_list("lesson_number", flat=True))

        for start_time in sessions.values_list("start_time", flat=True):
            label1.append(start_time.strftime("%d/%m/%y"))

        for session in sessions.all():
            c = 0
            w = 0
            n = 0
            for question in session.questions.all():
                if question.correct_answer:
                    c = c + question.answers.filter(correct=True).count()
                    w = w + question.answers.filter(correct=False).count()
                    n = n + question.no_answers
            correct.append(c)
            wrong.append(w)
            none.append(n)
        context = {
            'subject_code': subject_code,
            'label1': label1,
            'label2': label2,
            'connected': connected,
            'correct': correct,
            'wrong': wrong,
            'none': none
        }
        return render(request, 'user/subject_graphs.html', context)
    else:
        return HttpResponseBadRequest


@login_required
def session_graphs(request, subject_code, session_id):
    if request.method == "GET":
        q_labels = []
        a_correct = []
        a_wrong = []
        a_none = []
        feedback = {}
        session = request.user.taught_session.get(subject_code=subject_code, session_id=session_id)
        messages = session.messages.all().annotate(likes_count=Count('likes')).order_by('-likes_count')

        for question in session.questions.all().order_by("label"):
            if question.correct_answer:
                q_labels.append(question.label)
                a_correct.append(question.answers.filter(correct=True).count())
                a_wrong.append(question.answers.filter(correct=False).count())
                a_none.append(question.no_answers)
            else:
                index = question.text
                feedback[index] = list(question.answers.values_list("text").annotate(count=Count('text')).distinct().order_by("-count"))

        context = {
            'session_id': session_id,
            'subject_code': subject_code,
            'q_labels': q_labels,
            'a_correct': a_correct,
            'a_wrong': a_wrong,
            'a_none': a_none,
            'feedback': feedback,
            'messages': messages
        }
        return render(request, 'user/session_graphs.html', context)
