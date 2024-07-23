from django.urls import path

from . import views

urlpatterns = [
    path("dict", views.translate_dict, name="translate"),
    # path("string", views.html_translate_string, name="html_translate_string"),
]