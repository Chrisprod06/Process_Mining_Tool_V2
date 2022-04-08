from django.urls import path
from . import views

app_name = "landing_page"

urlpatterns = [
    # Crud urls
    path("", views.start_page, name="start_page"),
]
