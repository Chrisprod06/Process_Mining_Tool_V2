from django.urls import path
from . import views

urlpatterns = [
    path("view_process_models/", views.view_process_models, name="view_process_models")

]
