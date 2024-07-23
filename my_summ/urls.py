from django.urls import path

from . import views

urlpatterns = [
    path("", views.sentence_rank, name="sentence_rank"),
    path("from_dict", views.sentence_rank_from_dict, name="sentence_rank_from_dict"),
    path("from_dict_zh", views.sentence_rank_from_dict_zh, name="sentence_rank_from_dict_zh"),
    path("from_dict_ks", views.sentence_rank_ks, name="sentence_rank_ks"),
]
