from django.test import TestCase
from ..forms import QuizForm


class QuizFormTests(TestCase):
    """Tests for :class:`~MCQuizApp.forms.QuizForm`."""

    def test_valid_data(self):
        form = QuizForm(
            data={"title": "Test", "description": "Desc", "pass_mark": 50, "draft": False}
        )
        self.assertTrue(form.is_valid())

    def test_invalid_pass_mark(self):
        form = QuizForm(
            data={"title": "Test", "description": "Desc", "pass_mark": 150, "draft": False}
        )
        self.assertFalse(form.is_valid())
