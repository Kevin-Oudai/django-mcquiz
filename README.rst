====================
Multiple Choice Quiz
====================

MCQuiz is a Django app to display multiple choice quizzes and grade the quiz when it is submitted. It does not save any user data. It is strictly to create, display and grade.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "MCQuizApp" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'MCQuizApp',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('quiz/', include('MCQuizApp.urls')),

3. Run ``python manage.py migrate`` to create the mcquiz models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a quiz and questions (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/quiz/ to view the available quizzes.