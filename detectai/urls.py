from django.urls import path
from . import views

app_name = 'detectai'
urlpatterns = [
    path("front", views.front, name="front_page"),
    path("loglikely", views.loglikely, name="loglikely"),
    path("overlapwithwords", views.overlapwithwords, name="overlapwithwords"),
    path("SGDClassifier", views.SGDClassifier, name="SGDClassifier"),
    path("gpt_finetune", views.gpt_finetune, name="gpt_finetune"),
]
