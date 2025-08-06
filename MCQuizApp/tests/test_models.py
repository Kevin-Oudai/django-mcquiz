from django.core.exceptions import ValidationError
from django.test import TestCase
from ..models import Quiz, Question, Answer


def msg(test, expected):
    return "\nTest Returned: {} \nExpected: {}".format(test, expected)


class QuizModelTests(TestCase):

    def setUp(self):
        # Quizzes
        self.q1 = Quiz.objects.create(
            id=1,
            title="Test Quiz",
            description="Test Description"
        )
        self.q2 = Quiz.objects.create(
            id=2,
            title="Test Quiz 2",
            description="Test Description 2"
        )
        self.q3 = Quiz.objects.create(
            id=3,
            title="Test Quiz 3",
            description="Test Description 3"
        )

        # Questions associated with Quiz 1 (self.q1)
        self.p1 = Question.objects.create(
            content="quiz 1 question 1 content", hasAnswer=True)
        self.p2 = Question.objects.create(
            content="quiz 1 question 2 content", hasAnswer=True)
        self.p3 = Question.objects.create(
            content="quiz 3 question 3 content", hasAnswer=True)
        self.p4 = Question.objects.create(content="quiz 3 question 2 content")
        self.p1.quiz.add(self.q1)
        self.p2.quiz.add(self.q1)
        self.p3.quiz.add(self.q3)
        self.p4.quiz.add(self.q3)

    def test_quiz_url_creation(self):
        """
        This test ensures that when a new quiz is made the url for the quiz is generated from the title.
        """
        expected = "test-quiz"
        self.assertEqual(self.q1.url, expected,
                         "Did not create correct url.")

    def test_get_questions_with_zero_questions(self):
        """
        This test ensures that when no questions are connected with a quiz None is returned.
        """
        expected = None
        test = self.q2.get_questions()
        msg = "\nTest Returned: {} \nExpected: {}".format(test, expected)
        self.assertEqual(
            test, expected, msg)

    def test_get_questions_with_many_questions(self):
        """
        This test ensures that get_questions() returns the correct number of questions.
        """
        expected = 2
        test = len(self.q1.get_questions())
        msg = "\nTest Returned: {} \nExpected: {}".format(test, expected)
        self.assertEqual(test, expected, msg)

    def test_update_number_of_questions(self):
        """
        This test ensures that the number of questions attribute in the quiz is updated everytime a new question is associated with the quiz.
        """
        self.q1.save()
        expected = 2
        test = self.q1.number_of_questions
        msg = "\nTest Returned: {} \nExpected: {}".format(test, expected)
        self.assertEqual(test, expected, msg)

        self.q2.save()
        expected = 0
        test = self.q2.number_of_questions
        msg = "\nTest Returned: {} \nExpected: {}".format(test, expected)
        self.assertEqual(test, expected, msg)

    def test_pass_mark_default_equal_zero(self):
        """
        This test ensures that the default pass mark for any quiz is equal to zero.
        """
        expected = 0
        test = self.q1.pass_mark
        self.assertEqual(test, expected, msg(test, expected))

    def test_pass_mark_cannot_be_greater_than_100(self):
        """
        This test ensures that the pass mark can never be greater than 100.
        """
        expected = ValidationError
        self.q1.pass_mark = 200
        with self.assertRaises(expected):
            self.q1.save()

    def test_get_questions_returns_valid_questions(self):
        """
        This test ensures that get questions only returns questions with valid answers for the quiz.
        """
        questions = self.q3.get_questions()
        expected = [self.p3]
        self.assertQuerySetEqual(questions, expected)

    def test_quiz_creation(self):
        """A quiz can be created with the required fields."""
        quiz = Quiz.objects.create(title="Sample", description="Desc")
        self.assertEqual(str(quiz), "Sample")


class QuestionModelTests(TestCase):

    def setUp(self):
        """
        This is the initial setup conditions for the Question Model Tests.
        """
        self.problem = Question.objects.create(id=1, content="question 1")
        self.answer = Answer.objects.create(
            id=1, question=self.problem, content="answer 1")

    def test_for_no_correct_answer_to_a_question(self):
        """
        This test ensures that a question hasAnswer attribute returns False when there is no correct answer.
        """
        expected = False
        test = self.problem.hasAnswer
        self.assertIs(test, expected, msg(test, expected))

    def test_for_one_correct_answer_to_a_question(self):
        """
        This test ensures that the hasAnswer attribute changes to True when a correct answer is assigned.
        """
        self.answer1 = Answer.objects.create(
            id=2, question=self.problem, content="answer 2")
        self.answer1.save()
        test = self.problem.hasAnswer
        self.assertIs(test, False)
        self.answer2 = Answer.objects.create(
            id=3, question=self.problem, content="answer 3", correct=True)
        self.answer1.save()
        test = self.problem.hasAnswer
        self.assertIs(test, True)
