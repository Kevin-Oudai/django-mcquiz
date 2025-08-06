====================
Multiple Choice Quiz
====================

MCQuiz is a reusable Django application for building and running multiple
choice quizzes. The app provides models for quizzes, questions and answers,
views to take a quiz and review solutions, and Bootstrap-based templates for a
simple UI. MCQuiz does not store user information; it simply displays quizzes,
accepts answers and calculates scores.

Features
--------

1. Create Quiz (in admin view)
2. Display Quiz List (user view)
3. Display Quiz Detail (user view)
4. Display Quiz with Images (user view - recommend using svg files)
5. Display Solutions and Score.

Requirements
------------

You require the following packages to use django-mcquiz.

1. django-latexify
2. python-slugify

They should be installed when you install django-mcquiz. You should also have you MEDIA_ROOT and MEDIA_URL configured. 

Quick start
-----------

1. Add "MCQuizApp" and "latexify" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        "MCQuizApp",
        "latexify",
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('quiz/', include('MCQuizApp.urls')),

3. In the HTML header to your template, include::

    {% include "latexify/stylesheets.html" %}

4. In the bottom of your HTML body, include the following to load the JS associated with latexify::
    
    {% include "latexify/scripts.html" %}

5. Run ``python manage.py migrate`` to create the mcquiz models.

6. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a quiz and questions (you'll need the Admin app enabled).

7. Visit http://127.0.0.1:8000/quiz/ to view the available quizzes.

Setup
-----

1. Install dependencies::

       pip install -r requirements.txt

2. Apply migrations::

       python manage.py migrate

3. Run the development server::

       python manage.py runserver

Usage
-----

* Log into the Django admin at ``/admin`` to create ``Quiz`` and ``Question``
  objects.
* Each question can have multiple answers with one marked as correct.
* Visit ``/quiz/`` to list quizzes and start answering questions.

Testing
-------

Run the test suite with coverage::

    coverage run manage.py test
    coverage report

License
-------

This project is licensed under the MIT License. You are free to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the
software provided that the copyright notice and permission notice are included
in all copies or substantial portions of the software. See ``LICENSE`` for the
full text.
