from django.http.response import Http404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.http import Http404

from .models import Quiz, Question, Answer


class QuizListView(ListView):
    model = Quiz
    context_object_name = 'quizzes'
    queryset = Quiz.objects.filter(
        number_of_questions__gt=0).filter(draft=False)


class QuizDetailView(DetailView):
    model = Quiz

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Quiz, pk=pk, draft=False)


def questions_view(request, pk, quiz_url):
    template_name = "MCQuizApp/question_list.html"
    data = []
    context = {}
    quiz = get_object_or_404(Quiz, id=pk)
    questions = quiz.get_questions()
    if not questions:
        raise Http404("no questions in the quiz.")
    context['title'] = quiz.title
    if questions != None:
        for i in range(len(questions)):
            data.append({
                "id": questions[i].pk,
                "figure": questions[i].figure,
                "content": questions[i].content,
                "answers": questions[i].get_answers_list()
            })
    context['questions'] = data
    context['pk'] = pk
    context['url'] = quiz_url
    response = render(request, template_name, context)
    return response


def solutions(request, pk, quiz_url):
    # retrive guesses
    guesses = request.GET.dict()
    # retrieve questions ids and correct answers
    questions = Quiz.objects.get(id=pk).get_questions()

    # create solutions list
    question = []
    for item in questions:
        if str(item.id) in guesses.keys():
            guess = guesses[str(item.id)]
        else:
            guess = None
        question.append({'figure': item.figure, 'content': str(item.content), 'guess': guess,
                         'answer': str(item.get_answer_id()), 'choices': item.get_answers_list()})
    # count total correct and total incorrect
    total_correct = 0
    total_incorrect = 0
    for item in question:
        if item['guess'] == item['answer']:
            total_correct += 1
        else:
            total_incorrect += 1

    # calculate percentage
    total_questions = len(questions)
    percentage = total_correct / total_questions * 100
    context = {}
    context['questions'] = question
    context['total'] = total_correct
    context['score'] = percentage
    context['errors'] = total_incorrect
    context['number'] = total_questions
    return render(request, 'MCQuizApp/solutions.html', context)
