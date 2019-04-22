from django.test import TestCase
from .models import User, Subject, Lesson, Question, QuestionChoice


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testUser", password="testPassword12345")

    def test_login(self):
        login = self.client.login(username="testUser", password="testPassword12345")
        self.assertEqual(login, True)

    def test_subject(self):
        Subject.objects.create(user=self.user, code="testCode", name="testName")
        self.assertEqual(self.user.subjects.count(), 1)