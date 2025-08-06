from django import forms
from .models import Quiz


class QuizForm(forms.ModelForm):
    """Form for creating and updating :class:`~MCQuizApp.models.Quiz` objects."""

    class Meta:
        model = Quiz
        fields = ["title", "description", "pass_mark", "draft"]

    def clean_pass_mark(self):
        """Ensure the pass mark is within 0 and 100."""
        mark = self.cleaned_data.get("pass_mark")
        if mark is not None and (mark < 0 or mark > 100):
            raise forms.ValidationError("Pass mark must be between 0 and 100.")
        return mark
