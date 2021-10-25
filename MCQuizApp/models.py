from django.conf.urls import url
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MaxValueValidator
from slugify import slugify as makeSlug


class Quiz(models.Model):
    title = models.CharField(verbose_name='Title', max_length=60, blank=False)
    description = models.TextField(verbose_name="Description", blank=True)
    url = models.SlugField(max_length=60, blank=True)
    number_of_questions = models.PositiveSmallIntegerField(
        blank=True, default=0, null=True, verbose_name="# of Questions")
    pass_mark = models.PositiveSmallIntegerField(
        blank=True, default=0, verbose_name="Pass Mark", validators=[MaxValueValidator(100)])
    draft = models.BooleanField(
        blank=True, default=False, verbose_name="Draft")

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
    """
    Attribute definition for the Question model
    quiz    -   Relates the quizzes and questions with a many to many field since a question can repeat in many quizzes
                and many quizzes can have the same question
    figure  -   If the question has a figure we use this attribute it may be blank (will add to future version).
    content -   This holds the text content for the question.
    reason  -   This holds the reason for the answer. It should be displayed after the question is answered.
    hasAnswer - This is set to true if the question has an answer.
    """
    quiz = models.ManyToManyField(Quiz, verbose_name="Quiz", blank=True)
    # figure = models.ImageField(
    #     upload_to='uploads/', blank=True, null=True, verbose_name="Figure")
    content = models.TextField(max_length=1000, blank=False,
                               help_text="Enter the question text.", verbose_name='Question')
    reason = models.TextField(
        max_length=2000, blank=True, help_text="Explanation for when question is answered.", verbose_name="Explanation")
    hasAnswer = models.BooleanField(default=False, verbose_name="Has Answer")

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
    """
    question    -   Relates multiple answers to one question.
    content     -   Contains the content for the answer
    correct     -   If this is the correct answer for a related question it should hold True and False otherwise.
    """
    question = models.ForeignKey(
        Question, verbose_name="Question", on_delete=models.CASCADE)
    content = models.CharField(max_length=1000, blank=False,
                               help_text="This contains the answer", verbose_name="Content")
    correct = models.BooleanField(
        blank=False, default=False, help_text="Set to this if the answer is correct")

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
