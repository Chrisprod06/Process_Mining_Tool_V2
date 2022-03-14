from django.urls import path
from . import views

app_name = "data_handling"
urlpatterns = [
    path("event_log_list/", views.event_log_list, name="event_log_list"),
    path("event_log_create/", views.event_log_create, name="event_log_create"),
    path("event_log_update/<str:pk>/", views.event_log_update, name="event_log_update"),
    path("event_log_detail/<str:pk>/", views.event_log_detail, name="event_log_detail"),
    path("event_log_delete/<str:pk>/", views.event_log_delete, name="event_log_delete")
]
