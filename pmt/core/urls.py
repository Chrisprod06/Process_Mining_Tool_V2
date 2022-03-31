from django.urls import path, include
from . import views

app_name = "core"
urlpatterns = [
    # Core app paths
    path("", views.index, name="index"),
    path("data_handling/", include("data_handling.urls")),
    path("process_handling/", include("process_handling.urls")),
]
