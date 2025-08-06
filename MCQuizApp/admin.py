from django.contrib import admin

from .models import Quiz, Question, Answer


class ChoiceInline(admin.StackedInline):
    model = Answer
    extra = 4
    max_num = 4


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('content', 'hasAnswer')


admin.site.register(Question, QuestionAdmin)
admin.site.register(Quiz)
admin.site.register(Answer)
