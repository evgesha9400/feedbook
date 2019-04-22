from django.urls import path, re_path
from . import views

urlpatterns = [
    path('<int:session_id>', views.session, name='session'),
    path('subject/<int:s_id>/lesson/<int:l_id>', views.session, name='session_create'),
    path('<int:session_id>/answer', views.answer, name='answer')
]
