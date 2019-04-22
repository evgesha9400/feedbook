from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='user/login.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),

    # subjects
    path('subjects/', views.subjects, name='subjects'),
    path('subjects/add', views.add_subject, name='add_subject'),
    path('subjects/update/<int:s_id>', views.update_subject, name='update_subject'),
    path('subjects/delete/<int:s_id>', views.delete_subject, name='delete_subject'),

    # lessons
    path('subjects/<int:s_id>/lessons/', views.lessons, name='lessons'),
    path('subjects/<int:s_id>/lessons/add', views.add_lesson, name='add_lesson'),
    path('subjects/<int:s_id>/lessons/update/<int:l_id>', views.update_lesson, name='update_lesson'),
    path('subjects/<int:s_id>/lessons/delete/<int:l_id>', views.delete_lesson, name='delete_lesson'),

    # questions
    path('subjects/<int:s_id>/lessons/<int:l_id>/questions', views.questions, name='questions'),
    path('subjects/<int:s_id>/lessons/<int:l_id>/questions/add', views.add_question, name='add_question'),
    path('subjects/<int:s_id>/lessons/<int:l_id>/questions/update/<int:q_id>',
         views.update_question, name='update_question'),
    path('subjects/<int:s_id>/lessons/<int:l_id>/questions/delete/<int:q_id>',
         views.delete_question, name='delete_question'),

    # session
    path('connect_to_session/', views.connect_to_session, name='connect_to_session'),

    # statistics
    path('statistics/', views.statistics, name='statistics'),
    path('statistics/<str:subject_code>', views.subject_statistics, name='subject_statistics'),

    # graphs
    path('statistics/<str:subject_code>/graph', views.subject_graphs, name='subject_graphs'),
    path('statistics/<str:subject_code>/<int:session_id>/graph', views.session_graphs, name='session_graphs')
]
