from django.http.response import Http404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404, render
from django.http import Http404

from .models import Quiz


class QuizListView(ListView):
    """Display a list of published quizzes.

    **HTTP method:** ``GET``

    **Context:**
        ``quizzes`` -- queryset of quizzes with at least one question.

    **Template:** ``MCQuizApp/quiz_list.html`` (via :class:`ListView`)
    """

    model = Quiz
    context_object_name = "quizzes"
    queryset = Quiz.objects.filter(number_of_questions__gt=0).filter(draft=False)


class QuizDetailView(DetailView):
    """Show details for a single quiz.

    **HTTP method:** ``GET``

    **Context:**
        ``quiz`` -- quiz instance specified by ``pk``

    **Template:** ``MCQuizApp/quiz_detail.html``
    """

    model = Quiz

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        return get_object_or_404(Quiz, pk=pk, draft=False)


def questions_view(request, pk, quiz_url):
    """Display the questions for a quiz and accept answers.

    **HTTP method:** ``GET``

    **Context:**
        ``title`` -- quiz title
        ``questions`` -- list of dictionaries for each question
        ``pk`` -- quiz primary key
        ``url`` -- quiz slug

    **Template:** ``MCQuizApp/question_list.html``
    """

    template_name = "MCQuizApp/question_list.html"
    data = []
    context = {}
    quiz = get_object_or_404(Quiz, id=pk)
    questions = quiz.get_questions()
    if not questions:
        raise Http404("no questions in the quiz.")
    context["title"] = quiz.title
    if questions is not None:
        for question in questions:
            data.append(
                {
                    "id": question.pk,
                    "figure": question.figure,
                    "content": question.content,
                    "answers": question.get_answers_list(),
                }
            )
    context["questions"] = data
    context["pk"] = pk
    context["url"] = quiz_url
    response = render(request, template_name, context)
    return response


def solutions(request, pk, quiz_url):
    """Display results for a submitted quiz.

    **HTTP method:** ``GET`` with answer parameters in query string.

    **Context:**
        ``questions`` -- list containing question data and guesses
        ``total`` -- number of correct answers
        ``score`` -- percentage score
        ``errors`` -- number of incorrect answers
        ``number`` -- total number of questions

    **Template:** ``MCQuizApp/solutions.html``
    """

    guesses = request.GET.dict()
    questions = Quiz.objects.get(id=pk).get_questions()

    question = []
    for item in questions:
        if str(item.id) in guesses.keys():
            guess = guesses[str(item.id)]
        else:
            guess = None
        question.append(
            {
                "figure": item.figure,
                "content": str(item.content),
                "guess": guess,
                "answer": str(item.get_answer_id()),
                "choices": item.get_answers_list(),
            }
        )

    total_correct = 0
    total_incorrect = 0
    for item in question:
        if item["guess"] == item["answer"]:
            total_correct += 1
        else:
            total_incorrect += 1

    total_questions = len(questions)
    percentage = total_correct / total_questions * 100
    context = {}
    context["questions"] = question
    context["total"] = total_correct
    context["score"] = percentage
    context["errors"] = total_incorrect
    context["number"] = total_questions
    return render(request, "MCQuizApp/solutions.html", context)
