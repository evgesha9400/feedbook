from django.contrib.auth.decorators import login_required
from django.http import QueryDict, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.db.models import Count
from .models import Session, Message, Answer
from user.models import Lesson, Subject, Question
import random


@login_required
def session(request, session_id='', s_id='', l_id=''):
    if request.method == "GET":
        s = Session.objects.get(session_id=session_id)
        messages = s.messages.all().annotate(likes_count=Count('likes')).order_by('-likes_count')
        if request.user == s.teacher:
            subject = request.user.subjects.get(name=s.subject_name)
            lesson = subject.lessons.get(number=s.lesson_number)
            return render(request, 'session/session.html', dict(session=s, lesson=lesson, messages=messages))
        return render(request, 'session/session.html', dict(session=s, messages=messages))
    elif request.method == "POST":
        try:
            subject = request.user.subjects.get(pk=s_id)
            lesson = subject.lessons.get(pk=l_id)
        except Subject.DoesNotExist:
            return redirect('subjects')
        except Lesson.DoesNotExist:
            return redirect('lessons', s_id)
        session_id = generate_session_id()
        s = Session.objects.create(session_id=session_id, teacher=request.user, subject_code=subject.code,
                                   subject_name=subject.name, lesson_number=lesson.number)

        return redirect('session', session_id=s.session_id)
    else:
        return HttpResponseBadRequest


@login_required
def answer(request, session_id):
    if request.is_ajax() and request.method == "POST":
        try:
            session = request.user.connected_session.get(session_id=session_id)
            question = session.questions.get(pk=request.POST.get('q_id'))
            a_text = request.POST.get('text').lower().strip()
        except Session.DoesNotExist:
            return JsonResponse(dict(response="You are not the student"))
        except Question.DoesNotExist:
            return JsonResponse(dict(response="Question not found"))

        if question.correct_answer is None:
            correct = None
        else:
            correct = question.correct_answer.lower().strip() == a_text

        Answer.objects.create(question=question, text=a_text, correct=correct)

        return JsonResponse(dict(response=True))
    else:
        return JsonResponse(dict(response=False))


def generate_session_id():
    session_id = random.randint(999, 999999)
    try:
        Session.objects.get(session_id=session_id)
        generate_session_id()
    except Session.DoesNotExist:
        return session_id


