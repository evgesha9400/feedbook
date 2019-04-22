from .models import Session, Message, SessionQuestion
from user.models import QuestionChoice

from channels.generic.websocket import AsyncWebsocketConsumer
from django.core import serializers
from django.db.models import Count
import json


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = self.scope['url_route']['kwargs']['session_id']

    async def connect(self):
        print("connecting")

        await self.channel_layer.group_add(
            self.session_id,
            self.channel_name
        )

        session = Session.objects.get(session_id=self.session_id)
        if not session.teacher == self.scope['user']:
            session.connected_users.add(self.scope['user'])
            user_count = session.connected_users.count()
            session.user_count = user_count
            session.save()
            await self.channel_layer.group_send(self.session_id, {
                'type': 'users_change',
                'user_count': user_count
            })

        await self.accept()

    async def disconnect(self, close_code):
        print("disconnecting")

        user = self.scope['user']
        session = Session.objects.get(session_id=self.session_id)
        session.connected_users.remove(user)
        user_count = session.connected_users.count()
        await self.channel_layer.group_send(self.session_id, {
            'type': 'users_change',
            'user_count': user_count
        })
        await self.channel_layer.group_discard(
            self.session_id,
            self.channel_name
        )

    async def receive(self, text_data):

        data_json = json.loads(text_data)
        request_type = data_json['request_type']

        if request_type == "message":
            text = data_json['text']
            session = Session.objects.get(session_id=self.session_id)
            message = Message.objects.create(user=self.scope['user'], session=session, text=text)

            await self.channel_layer.group_send(self.session_id, {
                'type': 'message',
                'id': message.id,
                'text': text,
                'likes': 0
            })
        elif request_type == "timer":
            await self.channel_layer.group_send(self.session_id, {
                'type': 'timer',
                'seconds': data_json['seconds']
            })
        elif request_type == "like":

            pk = data_json['id']
            message = Message.objects.get(pk=pk)

            if self.scope['user'] in message.likes.all():
                message.likes.remove(self.scope['user'])
            else:
                message.likes.add(self.scope['user'])

            await self.channel_layer.group_send(self.session_id, {
                'type': 'like',
                'id': pk,
                'likes': message.likes.count()
            })

        elif request_type == "ask":
            session = Session.objects.get(session_id=self.session_id)
            subject = self.scope['user'].subjects.get(name=session.subject_name)
            lesson = subject.lessons.get(number=session.lesson_number)
            question = lesson.questions.get(pk=data_json['id'])
            choices = question.choices.all()
            try:
                correct = question.choices.get(correct=True).text
            except QuestionChoice.DoesNotExist:
                correct = None

            sq = SessionQuestion(session=session, id=question.id, label=question.label, mcq=(choices.count() > 1),
                                 text=question.text, correct_answer=correct)
            sq.save()
            data = {
                'type': 'ask_question',
                'question': serializers.serialize('json', [question]),
                'choices': serializers.serialize('json', choices)
                }
            await self.channel_layer.group_send(self.session_id, data)
        elif request_type == "answer_poll":
            q_id = data_json['q_id']
            session = Session.objects.get(session_id=self.session_id)
            question = session.questions.get(id=q_id)
            answers = list(question.answers.values_list("text")
                           .annotate(count=Count('text')).distinct().order_by("-count"))
            data = {'type': 'answer_poll',
                    'answers': answers
                    }
            await self.channel_layer.group_send(self.session_id, data)
        elif request_type == 'close':
            user = self.scope['user']
            print(type(self.session_id))
            try:
                session = user.taught_session.get(session_id=self.session_id)
                session.close()
                data = {'type': 'disconnect_all'}
                await self.channel_layer.group_send(self.session_id, data)
            except Session.DoesNotExist:
                pass

    async def message(self, event):
        await self.send(text_data=json.dumps({
            'response_type': 'message',
            'id': event['id'],
            'text': event['text'],
            'likes': event['likes']
        }))

    async def like(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'response_type': 'like',
            'id': event['id'],
            'likes': event['likes']
        }))

    async def ask_question(self, event):
        await self.send(text_data=json.dumps({
            'response_type': 'ask',
            'question': event['question'],
            'choices': event['choices']
        }))

    async def users_change(self, event):
        await self.send(text_data=json.dumps({
            'response_type': 'users_change',
            'user_count': event['user_count']
        }))

    async def disconnect_all(self, event):
        await self.send(text_data=json.dumps({
            'response_type': 'disconnect'
        }))

    async def timer(self, event):
        await self.send(text_data=json.dumps({
            'response_type': 'timer',
            'seconds': event['seconds']
        }))

    async def answer_poll(self, event):
        await self.send(text_data=json.dumps({
            'response_type': 'answer_poll',
            'answers': event['answers']
        }))

