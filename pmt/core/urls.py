from django.urls import path, include
from . import views

urlpatterns = [
    # Core app paths
    path("index/", views.index, name="index"),
    path("data_handling/", include("data_handling.urls")),
    path("process_handling/", include("process_handling.urls")),
]
