from django.utils import timezone
from user.models import User, Subject, Question
from django.db import models


class Session(models.Model):
    session_id = models.PositiveIntegerField(db_index=True, verbose_name="Session ID")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="taught_session")
    connected_users = models.ManyToManyField(User, related_name="connected_session", blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(default=None, null=True)
    live = models.BooleanField(default=True)
    subject_code = models.CharField(max_length=10)
    subject_name = models.CharField(max_length=60)
    lesson_number = models.PositiveSmallIntegerField(default="1")
    user_count = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return '%s' % self.session_id

    def close(self):
        self.end_time = timezone.now()
        self.live = False
        for question in self.questions.all():
            user_count = self.user_count
            answers_count = question.answers.count()
            if user_count >= answers_count:
                question.no_answers = self.user_count - question.answers.count()
            question.save()
        self.save()


class SessionQuestion(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE,
                                related_name="questions", related_query_name="question")
    label = models.CharField(max_length=8)
    text = models.CharField(max_length=255)
    mcq = models.BooleanField(default=True)
    correct_answer = models.CharField(max_length=255, null=True, default=None, blank=True)
    no_answers = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.text


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="messages",
                             related_query_name="message", null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="messages",
                                related_query_name="message")
    likes = models.ManyToManyField(User, related_name="liked_messages",
                                   related_query_name="liked_message", blank=True)
    text = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(SessionQuestion, on_delete=models.CASCADE,
                                 related_name="answers", related_query_name="answer")
    text = models.CharField(max_length=255)
    correct = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.text
