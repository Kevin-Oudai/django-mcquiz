from django.urls import path, include
from . import views

app_name = 'mcquiz'
urlpatterns = [
    path('', views.QuizListView.as_view(), name='index'),
    path('<int:pk>/<slug:quiz_url>',
         views.QuizDetailView.as_view(), name='quiz-detail'),
    path('<int:pk>/<slug:quiz_url>/questions',
         views.questions_view, name='question-list'),
    path('<int:pk>/<slug:quiz_url>/solutions',
         views.solutions, name='solutions'),
]
