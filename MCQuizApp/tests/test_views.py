from django.urls import reverse
from django.test import TestCase
from ..models import Quiz, Question, Answer


def create_quiz(id, title, description, draft=False):
    """
    Create a quiz with a given title and decription.
    """
    return Quiz.objects.create(id=id, title=title, description=description, draft=draft)


def create_question(id, content, hasAnswer=True):
    """
    Create a question with a given content.
    """
    return Question.objects.create(id=id, content=content, hasAnswer=hasAnswer)


def create_answer(id, question, content, correct=False):
    """
    Create a answer with a given content.
    """
    return Answer.objects.create(id=id, question=question, content=content, correct=correct)


class QuizListViewTests(TestCase):
    """
    This class deals with all tests related to the QuizListView class in views.py.
    name='index'
    """

    def test_no_quiz(self):
        """
        This test ensures that when no quiz exists a message is displayed to reflect that.
        """
        response = self.client.get(reverse('mcquiz:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No quizzes yet.")
        self.assertQuerySetEqual(response.context['quizzes'], [])

    def test_quiz_list_view_displays_quiz(self):
        """The quiz list view loads and lists available quizzes."""
        quiz = create_quiz(1, "Title", "Desc")
        question = create_question(1, "Question", True)
        question.quiz.add(quiz)
        create_answer(1, question, "Ans", True)
        response = self.client.get(reverse('mcquiz:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Title")

    def test_draft_quiz(self):
        """
        This test ensures that no draft quizzes are returned in the quizzes context
        """
        quiz1 = create_quiz(1, "Test Title 1", "Test Description 1", True)
        response = self.client.get(reverse('mcquiz:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No quizzes yet.")
        self.assertQuerySetEqual(response.context['quizzes'], [])

    def test_quiz_with_no_questions(self):
        """
        This test ensures that if a quiz has no questions associated with 
        it then it will not be present in the quizzes context variable.
        """
        quiz1 = create_quiz(1, "Test Title 1", "Test Description 1")
        response = self.client.get(reverse('mcquiz:index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Test Title 1")
        self.assertQuerySetEqual(response.context['quizzes'], [])


class QuizDetailViewTests(TestCase):
    """
    This deals with all tests related to the QuizDetailView class in views.py.
    name='quiz-detail'
    """

    def test_no_questions(self):
        """
        This test ensures that a 404 error is returned when a quiz has no questions
        associated with it.

        REASON: Although it will not show in the quizzes list it prevents
        anyone from trying a url and accessing the quiz.
        """
        quiz1 = create_quiz(1, "Test Title 1",
                            "Test Description 1", draft=False)
        url = reverse('mcquiz:quiz-detail', args=(quiz1.id, quiz1.url))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_draft_quiz(self):
        """
        This test ensures that a 404 error is returned when a quiz is a draft.
        Same as reason in test_no_questions.
        """
        quiz1 = create_quiz(1, "Test Title 1", "Test Description 1")
        url = reverse('mcquiz:quiz-detail', args=(quiz1.id, quiz1.url))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_none_draft_quiz(self):
        """
        This test ensures that none draft quizzes shows the quiz details.
        """
        quiz1 = create_quiz(1, "Test Title 1", "Test Description 1", False)
        question1 = create_question(1, "Question 1")
        question1.quiz.add(quiz1)
        create_answer(1, question1, "Test Answer 1", True)
        quiz1.draft = False
        quiz1.save()
        url = reverse('mcquiz:quiz-detail', args=(quiz1.id, quiz1.url))
        response = self.client.get(url)
        self.assertEqual(quiz1.number_of_questions, 1)
        self.assertIs(quiz1.draft, False)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Title 1")
        self.assertContains(response, "Test Description 1")


class Question_ViewTests(TestCase):
    """
    This deals with all tests related to the questions_view view function in views.py.
    name='question-list'
    """

    def test_no_questions(self):
        """
        This ensures that a when a quiz has no questions associated with it a 
        404 error is returned. Same reason as QuizDetailViewTests.test_no_questions().
        """
        quiz1 = create_quiz(1, "Test Title 1",
                            "Test Description 1", draft=False)
        url = reverse('mcquiz:question-list', args=(quiz1.id, quiz1.url))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_question_with_no_answer(self):
        """
        This ensures that if a question has no answers to choose it will not
        be displayed.
        """
        quiz1 = create_quiz(1, "Test Title 1",
                            "Test Description 1", draft=False)
        question1 = create_question(1, "Test Question 1", hasAnswer=False)
        question2 = create_question(2, "Test Question 2", hasAnswer=True)
        question1.quiz.add(quiz1)
        question2.quiz.add(quiz1)
        url = reverse('mcquiz:question-list', args=(quiz1.id, quiz1.url))
        response = self.client.get(url)
        self.assertContains(response, "Test Question 2")

    def test_quiz_with_questions_answers(self):
        """
        This ensures that if a quiz has questions it is displayed.
        """
        quiz1 = create_quiz(1, "Test Title 1",
                            "Test Description 1", draft=False)
        question1 = create_question(1, "Test Question 1")
        answer1 = create_answer(1, question1, "Test Answer 1", correct=True)
        question1.quiz.add(quiz1)
        url = reverse('mcquiz:question-list', args=(quiz1.id, quiz1.url))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Question 1")


class SolutionsTests(TestCase):
    """
    This deals with all tests related to the solutions view function in views.py.
    name='solutions'
    """

    def test_missing_answer(self):
        """
        This test ensures that when an answer is missing a valid response is still returned.
        """
        quiz1 = create_quiz(1, "Test Title 1",
                            "Test Description 1", draft=False)
        question1 = create_question(1, "Test Question 1")
        answer1 = create_answer(1, question1, "Test Answer 1", correct=True)
        question1.quiz.add(quiz1)
        url = "/quiz/1/test-title-1/solutions?"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_answer_is_correct(self):
        """
        This test ensures that when an answer is correct it is highlighted in green.
        """
        quiz1 = create_quiz(1, "Test Title 1",
                            "Test Description 1", draft=False)
        question1 = create_question(1, "Test Question 1")
        answer1 = create_answer(1, question1, "Test Answer 1", correct=True)
        question1.quiz.add(quiz1)
        url = "/quiz/1/test-title-1/solutions?1=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total Correct")
        self.assertContains(response, '<td class="text-end">1</td>')

        #

    def test_answer_is_incorrect(self):
        """
        This test ensures that if an answer is incorrect the incorrect answer is highlighted red
        and the correct answer is highlighted in green.
        """
        quiz1 = create_quiz(1, "Test Title 1",
                            "Test Description 1", draft=False)
        question1 = create_question(1, "Test Question 1")
        answer1 = create_answer(1, question1, "Test Answer 1", correct=True)
        answer2 = create_answer(2, question1, "Test Answer 2")
        question1.quiz.add(quiz1)
        url = "/quiz/1/test-title-1/solutions?1=2"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
