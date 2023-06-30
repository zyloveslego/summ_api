from django.urls import path

from . import views

urlpatterns = [
    path("", views.sentence_rank, name="sentence_rank"),
    path("from_dict", views.sentence_rank_from_dict, name="sentence_rank_from_dict"),
]
