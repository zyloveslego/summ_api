from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_essay_grade, name="get_essay_grade"),
]
