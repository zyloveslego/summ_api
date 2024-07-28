from django.urls import path
from . import views

app_name = 'ai_search'
urlpatterns = [
    path("", views.ai_search, name="ai_search"),
    # path("savetodb/", views.savetodb, name="savetodb"),
]