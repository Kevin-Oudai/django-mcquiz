from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MaxValueValidator
from slugify import slugify as makeSlug


class Quiz(models.Model):
    """Represents a collection of :class:`Question` objects.

    Fields
    ------
    title: :class:`~django.db.models.CharField`
        Human readable name for the quiz.
    description: :class:`~django.db.models.TextField`
        Optional description shown on the quiz detail page.
    url: :class:`~django.db.models.SlugField`
        Slug generated from ``title`` used in URLs.
    number_of_questions: :class:`~django.db.models.PositiveSmallIntegerField`
        Automatically populated count of associated questions.
    pass_mark: :class:`~django.db.models.PositiveSmallIntegerField`
        Percentage score required to pass the quiz. Must be <= 100.
    draft: :class:`~django.db.models.BooleanField`
        When ``True`` the quiz is hidden from public listings.
    """

    title = models.CharField(
        verbose_name="Title",
        max_length=60,
        help_text="Name of the quiz displayed to users.",
    )
    description = models.TextField(
        verbose_name="Description",
        blank=True,
        help_text="Optional description of the quiz.",
    )
    url = models.SlugField(
        max_length=60,
        blank=True,
        verbose_name="URL",
        help_text="Auto-generated slug for building quiz URLs.",
    )
    number_of_questions = models.PositiveSmallIntegerField(
        blank=True,
        default=0,
        null=True,
        verbose_name="# of Questions",
        help_text="Calculated number of questions in the quiz.",
    )
    pass_mark = models.PositiveSmallIntegerField(
        blank=True,
        default=0,
        verbose_name="Pass Mark",
        validators=[MaxValueValidator(100)],
        help_text="Required percentage score to pass (0-100).",
    )
    draft = models.BooleanField(
        blank=True,
        default=False,
        verbose_name="Draft",
        help_text="Designates whether this quiz is unpublished.",
    )

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def save(self, *args, **kwargs):
        self.url = makeSlug(self.title)
        if self.pass_mark > 100:
            raise ValidationError('{} is above 100'.format(self.pass_mark))
        if self.id:
            self.get_number_of_questions()
        super().save(*args, **kwargs)

    def get_questions(self):
        questions = self.question_set.filter(hasAnswer=True)
        if not questions:
            return None
        return questions

    def get_number_of_questions(self):
        questions = self.get_questions()
        if questions == None:
            self.number_of_questions = 0
            self.draft = True
        else:
            self.number_of_questions = len(questions)

    def __str__(self):
        return self.title


class Question(models.Model):
    """A single question that belongs to one or more quizzes.

    Fields
    ------
    quiz: :class:`~django.db.models.ManyToManyField`
        Relationship to the quizzes that include this question.
    figure: :class:`~django.db.models.FileField`
        Optional image associated with the question.
    content: :class:`~django.db.models.TextField`
        The question text.
    reason: :class:`~django.db.models.TextField`
        Explanation displayed when showing solutions.
    hasAnswer: :class:`~django.db.models.BooleanField`
        Indicates whether the question currently has a correct answer.
    """

    quiz = models.ManyToManyField(
        Quiz,
        verbose_name="Quiz",
        blank=True,
        help_text="Quizzes that include this question.",
    )
    figure = models.FileField(
        upload_to="quiz_images/",
        default=None,
        blank=True,
        null=True,
        verbose_name="Figure",
        help_text="Optional image displayed with the question.",
    )
    content = models.TextField(
        max_length=1000,
        blank=False,
        help_text="Enter the question text.",
        verbose_name="Question",
    )
    reason = models.TextField(
        max_length=2000,
        blank=True,
        help_text="Explanation displayed when the question is answered.",
        verbose_name="Explanation",
    )
    hasAnswer = models.BooleanField(
        default=False,
        verbose_name="Has Answer",
        help_text="True if a correct answer exists for this question.",
    )

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def check_if_correct(self, guess):
        """
        Returns True if the answer corresponding to the guess is correct.
        """
        answer = Answer.objects.get(id=guess)
        return answer.correct

    def get_answer_id(self):
        """
        Returns the id for the correct answer as a string.
        """
        answer_id = str(Answer.objects.filter(
            question=self, correct=True).values('id')[0]['id'])
        return answer_id

    def get_answers_list(self):
        """
        Returns a list of tuples for answers related to a question.
        tuple format (answer.id, answer.content, answer.correct)
        """
        answers = [(str(answer.id), answer.content, answer.correct)
                   for answer in Answer.objects.filter(question=self).order_by('?')]
        return answers

    def __str__(self):
        return self.content


class Answer(models.Model):
    """Possible answer for a :class:`Question`.

    Fields
    ------
    question: :class:`~django.db.models.ForeignKey`
        The question this answer relates to.
    content: :class:`~django.db.models.CharField`
        Text displayed for the answer.
    correct: :class:`~django.db.models.BooleanField`
        Indicates if this answer is the correct one.
    """

    question = models.ForeignKey(
        Question,
        verbose_name="Question",
        on_delete=models.CASCADE,
        help_text="Question that this answer belongs to.",
    )
    content = models.CharField(
        max_length=1000,
        blank=False,
        help_text="Text for the answer option.",
        verbose_name="Content",
    )
    correct = models.BooleanField(
        blank=False,
        default=False,
        help_text="Set to True if this answer is correct.",
    )

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'

    def save(self, *args, **kwargs):
        if self.correct:
            self.question.hasAnswer = True
            self.question.save()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.content
