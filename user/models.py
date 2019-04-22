from django.contrib.auth.models import User
from django.db import models


class Subject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subjects", related_query_name="subject")
    code = models.CharField(max_length=24)
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    number = models.PositiveSmallIntegerField(default=1)
    description = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,
                                related_name="lessons", related_query_name="lesson")

    def __str__(self):
        return str(self.number)


class Question(models.Model):
    label = models.CharField(max_length=8)
    text = models.CharField(max_length=255)
    image = models.ImageField(upload_to='questions', blank=True)
    timeout = models.PositiveSmallIntegerField(default=15)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE,
                               related_name="questions", related_query_name="question")

    class Meta:
        ordering = ['label']

    def __str__(self):
        return '{}?'.format(self.text)


class QuestionChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices",
                                 related_query_name="choice")
    text = models.CharField(max_length=150, verbose_name="Answer")
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
